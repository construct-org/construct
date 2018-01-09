# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import threading
import time
import timeit
import sys
from fstrings import f
from construct.core.globals import status
from construct.core.util import (
    get_callable_name,
    pop_attr,
    ensure_callable,
    ensure_instance
)
from construct.err import TimeoutError, ExtractorError
__all__ = [
    'TIMER',
    'SLEEP',
    'Async',
    'AsyncRequest',
    'AsyncTask',
    'Request',
    'Task',
    'task',
    'ready_when',
    'skip_when',
    'extract',
    'inject',
    'priority',
    'available',
]


# Globals
DEFAULT_PRIORITY = 0

# Dependencies
TIMER = timeit.default_timer
SLEEP = time.sleep


class Async(threading.Thread):

    def __init__(self, fn, args=None, kwargs=None, retries=0, interval=1):
        super(Async, self).__init__()
        self.fn = fn
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.daemon = True
        self.retries = retries
        self.interval = interval
        self.status = status.WAITING
        self._exc = None
        self._value = None
        self._shutdown = threading.Event()
        self._stopped = threading.Event()
        self._started = threading.Event()

    def run(self):

        self._started.set()
        retries = 0

        try:

            while True:

                self.status = status.RUNNING

                try:
                    self._value = self.fn(*self.args, **self.kwargs)
                    self.status = status.SUCCESS
                    break

                except:
                    self._exc = sys.exc_info()
                    self.status = status.FAILED
                    if retries >= self.retries:
                        break

                retries += 1
                self._shutdown.wait(self.interval)

        finally:

            self._stopped.set()

    def started(self):
        return self._started.is_set()

    def stopped(self):
        return self._stopped.is_set()

    def stop(self):
        self._shutdown.set()
        self._stopped.wait()
        if self.isAlive():
            self.join()

    def ready(self):
        return self.status in status.DONE_STATUSES

    def _get_ready(self, propagate=True):

        if self.status == status.SUCCESS:
            return self._value

        if self.status == status.FAILED:
            if propagate:
                raise self._exc[0], self._exc[1], self._exc[2]
            return self._exc

    def get(self, timeout=None, interval=0.5, propagate=True):

        st = TIMER()
        while not self.ready():
            if timeout and TIMER() - st > timeout:
                raise TimeoutError('Result not ready yet...')
            SLEEP(interval)

        return self._get_ready(propagate)


class Request(object):

    def __init__(self, task, args, kwargs):
        self.task = task
        self.args = args
        self.kwargs = kwargs
        self.status = status.WAITING
        self.retries = 0
        self._exc = None
        self._value = None

    def ready(self):
        return self.status in status.DONE_STATUSES

    def get(self, propagate=True):

        self.status = status.RUNNING
        try:
            self._value = self.task(*self.args, **self.kwargs)
            self.status = status.SUCCESS
            return self._value
        except:
            self.retries += 1
            self._exc = sys.exc_info()
            self.status = status.FAILED
            if propagate:
                raise self._exc[0], self._exc[1], self._exc[2]
            return self._exc


class AsyncRequest(object):

    def __init__(self, thread, task, args, kwargs):
        self._thread = thread
        self.task = task
        self.args = args
        self.kwargs = kwargs
        self.retries = 0
        self._exc = None
        self._value = None

    @property
    def status(self):
        return self._thread.status

    def ready(self):
        return self._thread.ready()

    def stop(self):
        return self._thread.stop()

    def get(self, timeout=None, interval=0.5, propagate=True):

        if not self._thread.started():
            self._thread.start()

        return self._thread.get(timeout, interval, propagate)


class Task(object):

    def __init__(self, fn, identifier=None, description=None,
                 priority=DEFAULT_PRIORITY, ready_when=None, skip_when=None,
                 extract=None, inject=None, available=True):
        self.fn = fn
        self.priority = priority
        self.identifier = identifier
        self.description = description
        self.ready_when = ready_when or []
        self.skip_when = skip_when or []
        self._extract = extract
        self._inject = inject
        self._available = available

    def __repr__(self):
        return (
            'Task(identifier={}, fn={}, ready_when={}, skip_when={})'
        ).format(
            repr(self.identifier),
            self.fn,
            self.ready_when,
            self.skip_when
        )

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)

    def ready(self, ctx):

        if self.ready_when is None:
            return True

        for fn in self.ready_when:
            if not fn(ctx):
                return False

        return True

    def skip(self, ctx):

        if self.skip_when is None:
            return False

        for fn in self.skip_when:
            if fn(ctx):
                return True

        return False

    def extract(self, ctx):

        if self._extract is None:
            return (), {}

        return process_arguments(self._extract(ctx))

    def inject(self, ctx, result):

        if self._inject:
            self._inject(ctx, result)

    def available(self, ctx):

        if callable(self._available):
            return self._available(ctx)

        return self._available

    def request(self, *args, **kwargs):
        return Request(self, args, kwargs)


class AsyncTask(Task):

    def request(self, *args, **kwargs):
        async_thread = Async(self, args, kwargs)
        return AsyncRequest(async_thread, self, args, kwargs)


# Decorator interface for creating tasks


def task(identifier_or_fn, task_type=Task):
    '''Decorator that converts a function to a Task object. The function
    remains callable by normal means, but also receives the additional
    functionality of a Task object.

    Arguments:
        identifier_or_fn (str or callable): When a string is passed, return
            a decorator which passes the string to the Task object as it's
            identifier. If a callable is passed, use the callables name as
            the Task's identifier.

    Returns:
        Task
    '''

    if callable(identifier_or_fn):
        fn = identifier_or_fn
        return task_type(
            fn,
            identifier=get_callable_name(fn),
            description=fn.__doc__,
            ready_when=pop_attr(fn, '__task_ready_when__', []),
            skip_when=pop_attr(fn, '__task_skip_when__', []),
            extract=pop_attr(fn, '__task_extract__', None),
            inject=pop_attr(fn, '__task_inject__', None),
            priority=pop_attr(fn, '__task_priority__', 0)
        )

    if isinstance(identifier_or_fn, basestring):
        identifier = identifier_or_fn

        def wrapper(fn):
            return task_type(
                fn,
                identifier,
                description=fn.__doc__,
                ready_when=pop_attr(fn, '__task_ready_when__', []),
                skip_when=pop_attr(fn, '__task_skip_when__', []),
                extract=pop_attr(fn, '__task_extract__', None),
                inject=pop_attr(fn, '__task_inject__', None),
                priority=pop_attr(fn, '__task_priority__', 0)
            )
        return wrapper

    raise TypeError("Argument must be: Union[str, Callable[...]]")


def async_task(identifier_or_fn):
    '''Like :func:`task` decorator. This returns an AsyncTask which will be run
    in a separate thread when an Action is evaluated. Can still be called
    normally like a standard function.

    Arguments:
        identifier_or_fn (str or callable): When a string is passed, return
            a decorator which passes the string to the Task object as it's
            identifier. If a callable is passed, use the callables name as
            the Task's identifier.

    Returns:
        AsyncTask
    '''

    return task(identifier_or_fn, AsyncTask)


def ready_when(*funcs):

    [ensure_callable(func) for func in funcs]

    def wrapper(fn):
        if not hasattr(fn, '__task_ready_when__'):
            fn.__task_ready_when__ = []
        fn.__task_ready_when__.extend(funcs)
        return fn

    return wrapper


def skip_when(*funcs):

    [ensure_callable(func) for func in funcs]

    def wrapper(fn):
        if not hasattr(fn, '__task_skip_when__'):
            fn.__task_skip_when__ = []
        fn.__task_skip_when__.extend(funcs)
        return fn

    return wrapper


def priority(value):

    ensure_instance(value, int)

    def wrapper(fn):
        fn.__task_priority__ = value
        return fn

    return wrapper


def extract(func):

    ensure_callable(func)

    def wrapper(fn):
        fn.__task_extract__ = func
        return fn

    return wrapper


def inject(func):

    ensure_callable(func)

    def wrapper(fn):
        fn.__task_inject__ = func
        return fn

    return wrapper


def available(value):

    def wrapper(fn):
        fn.__task_available__ = value
        return fn

    return wrapper


def process_arguments(arguments):
    '''Process arguments returning args and kwargs.

    Acceptable arguments:
        tuple(tuple, dict) - args and kwargs
        tuple - just arguments
        dict(args=tuple, kwargs=dict) - dict with args and dict keys
        dict(**kwargs) - just a dict with keyword arguments
        dict(args, **kwrags) a dict with args and keyword arguments

    Parameters:
        arguments: tuple or dict containing args and kwargs

    Returns:
        tuple, dict: args and kwargs

    Raises:
        ExtractorError: when arguments does not match one of the above
            signatures
    '''
    if isinstance(arguments, tuple):
        if (
            len(arguments) == 2
            and isinstance(arguments[0], tuple)
            and isinstance(arguments[1], dict)
        ):
            args = arguments[0]
            kwargs = arguments[1]
        else:
            args = arguments
            kwargs = {}
    elif isinstance(arguments, dict):
        args = arguments.pop('args', ())
        if 'kwargs' in arguments:
            kwargs = arguments['kwargs']
        else:
            kwargs = arguments
    else:
        raise ExtractorError(
            'Unrecognized return value signature from extractor.\n',
            f('Got: {arguments}\n'),
            'Expected:\n',
            '    ((...), {...})\n',
            '    {...}\n',
            '    (...)\n',
            '    {"args": (...), "kwargs": {...}}\n',
        )
    return args, kwargs
