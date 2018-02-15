# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

__all__ = [
    'TIMER',
    'SLEEP',
    'RequestThread',
    'AsyncRequest',
    'AsyncTask',
    'Request',
    'Task',
    'task',
    'async_task',
    'requires',
    'skips',
    'extract',
    'inject',
    'available',
    'task_done',
    'task_failed',
    'task_success',
    'store_key',
    'artifacts_key',
]

import threading
import time
import timeit
import sys
from fstrings import f
from construct.constants import *
from construct.context import (
    context,
    _ctx_stack,
    request,
    _req_stack
)
from construct.util import (
    get_callable_name,
    pop_attr,
    ensure_callable,
    ensure_instance
)
from construct.types import Priority
from construct.err import TimeoutError, ExtractorError
from construct import signal


# Globals
DEFAULT_PRIORITY = Priority(0)

# Dependencies
TIMER = timeit.default_timer
SLEEP = time.sleep


class RequestThread(threading.Thread):

    def __init__(self, request, retries=0, interval=1):
        super(RequestThread, self).__init__()
        self.retries = retries
        self.interval = interval
        self.request = request
        self._shutdown = threading.Event()
        self._stopped = threading.Event()
        self._started = threading.Event()
        self.request.set_status(WAITING)

    def start(self):
        '''Pass context through to thread'''
        self.request.set_status(PENDING)
        super(RequestThread, self).start()

    def run(self):

        try:

            self._started.set()
            retries = 0
            self.request.push()

            while True:

                self.request.set_status(RUNNING)

                try:
                    self.request._before_get()
                    result = self.request.task(
                        *self.request.args,
                        **self.request.kwargs
                    )
                    self.request._after_get()
                    self.request.set_value(result)
                    break

                except:
                    self.request.set_exception(*sys.exc_info())
                    if retries >= self.retries:
                        break

                retries += 1
                if self._shutdown.wait(self.interval):
                    break

        finally:

            self.request.pop()
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
        return self.request._status in DONE_STATUSES

    def _get_ready(self, propagate=True):

        if self.request.success:
            return self.request._value

        if self.request.failed:
            exc = self.request._exc
            if propagate:
                raise exc[0], exc[1], exc[2]
            return exc

    def get(self, timeout=None, interval=0.2, propagate=True):

        st = TIMER()
        while not self.ready():
            if timeout is not None and TIMER() - st > timeout:
                raise TimeoutError('Result not ready yet...')
            SLEEP(interval)

        return self._get_ready(propagate)


class Request(object):

    def __init__(self, task, ctx=None, args=None, kwargs=None):
        self.task = task
        self.ctx = ctx
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.retries = 0
        self._enabled = True
        self._status = None
        self._exc = None
        self._value = None
        self.set_status(WAITING)

    def push(self):
        _ctx_stack.push(self.ctx)
        _req_stack.push(self)

    def pop(self):
        if _req_stack.top is self:
            _req_stack.pop()
        if _ctx_stack.top is self:
            _ctx_stack.pop()

    @property
    def value(self, value):
        return self._value

    def set_value(self, value):
        self._value = value
        self.set_status(SUCCESS)

    @property
    def exception(self):
        return self._exc

    def set_exception(self, *exc_info):
        self._exc = exc_info
        self.set_status(FAILED)

    @property
    def status(self):

        return self._status

    def set_status(self, status):

        if self._status == status:
            return

        last_status = status
        self._status = status
        signal.send('request.status.changed', self, last_status, status)

    @property
    def enabled(self):
        return self._enabled

    def set_enabled(self, value):
        self._enabled = value
        signal.send('request.enabled', self, self._enabled)

    @property
    def success(self):
        return self._status == SUCCESS

    @property
    def failed(self):
        return self._status == FAILED

    @property
    def done(self):
        return self.ready()

    @property
    def ready(self):
        return self._status in DONE_STATUSES

    def _before_get(self):
        if self.ctx is not None:
            self.args, self.kwargs = self.task.extract(self.ctx)

    def _after_get(self):
        if self.ctx is not None:
            self.task.inject(self.ctx, self._value)

    def get(self, propagate=True):

        if self.success:
            return self._value

        if self.failed:
            if propagate:
                raise self._exc[0], self._exc[1], self._exc[2]
            return self._exc

        self._before_get()
        self.set_status(RUNNING)

        try:

            self.push()
            result = self.task(*self.args, **self.kwargs)
            self._after_get()
            self.set_value(result)
            return self._value

        except:

            self.retries += 1
            exc_info = sys.exc_info()
            self.set_exception(*sys.exc_info())
            if propagate:
                raise exc_info[0], exc_info[1], exc_info[2]
            return exc_info

        finally:

            self.pop()


class AsyncRequest(Request):

    def __init__(self, task, ctx=None, args=None, kwargs=None):
        super(AsyncRequest, self).__init__(task, ctx, args, kwargs)
        self._thread = RequestThread(self)

    def get(self, timeout=None, interval=0.2, propagate=True):

        try:

            self.push()

            if not self._thread.started():
                self._thread.start()

            return self._thread.get(timeout, interval, propagate)

        finally:

            self.pop()


class Task(object):

    _request_cls = Request

    def __init__(self, fn, identifier=None, description=None,
                 priority=DEFAULT_PRIORITY, requires=None, skips=None,
                 extract=None, inject=None, available=True):
        self.fn = fn
        if not isinstance(priority, Priority):
            priority = Priority(priority)
        self.priority = priority
        self.identifier = identifier
        self.description = description
        self.requires = requires or []
        self.skips = skips or []
        self._extract = extract
        self._inject = inject
        self._available = available

    def __repr__(self):
        return (
            'Task(identifier={}, fn={}, requires={}, skips={})'
        ).format(
            repr(self.identifier),
            self.fn,
            self.requires,
            self.skips
        )

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)

    def ready(self, ctx):

        if self.requires is None:
            return True

        for fn in self.requires:
            if not fn(ctx):
                return False

        return True

    def skip(self, ctx):

        if self.skips is None:
            return False

        for fn in self.skips:
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

    def request(self, ctx=None, args=None, kwargs=None):
        return self._request_cls(self, ctx, args, kwargs)


class AsyncTask(Task):

    _request_cls = AsyncRequest


# Decorator interface for creating tasks


def task(identifier=None, priority=None, description=None, cls=Task):
    '''Decorator that converts a function to a Task object. The function
    remains callable by normal means, but also receives the additional
    functionality of a Task object.

    Arguments:
        identifier (str or callable): When a string is passed, return
            a decorator which passes the string to the Task object as it's
            identifier. If a callable is passed, use the callables name as
            the Task's identifier.
        priority (Priority or int): Priority used to order tasks in an action
        description (str): Defaults to the decorated functions docstring
        cls (Object): Task type to create, defaults to Task

    Returns:
        Task or instance of cls
    '''

    if callable(identifier):
        fn = identifier
        return cls(
            fn,
            identifier=get_callable_name(fn),
            description=description or fn.__doc__,
            requires=pop_attr(fn, '__task_requires__', []),
            skips=pop_attr(fn, '__task_skips__', []),
            extract=pop_attr(fn, '__task_extract__', None),
            inject=pop_attr(fn, '__task_inject__', None),
            priority=priority if priority is not None else DEFAULT_PRIORITY
        )

    if isinstance(identifier, basestring) or identifier is None:
        identifier = identifier

        def wrapper(fn):
            return cls(
                fn,
                identifier or get_callable_name(fn),
                description=description or fn.__doc__,
                requires=pop_attr(fn, '__task_requires__', []),
                skips=pop_attr(fn, '__task_skips__', []),
                extract=pop_attr(fn, '__task_extract__', None),
                inject=pop_attr(fn, '__task_inject__', None),
                priority=priority if priority is not None else DEFAULT_PRIORITY
            )
        return wrapper

    raise TypeError("Argument must be: Union[str, Callable[...]]")


def async_task(identifier, priority=None, description=None, cls=AsyncTask):
    '''Like :func:`task` decorator. This returns an AsyncTask which will be run
    in a separate thread when an Action is evaluated. Can still be called
    normally like a standard function.

    Arguments:
        identifier (str or callable): When a string is passed, return
            a decorator which passes the string to the Task object as it's
            identifier. If a callable is passed, use the callables name as
            the Task's identifier.
        priority (Priority or int): Priority used to order tasks in an action
        description (str): Defaults to the decorated functions docstring
        cls (Object): Task type to create, defaults to AsyncTask

    Returns:
        AsyncTask or instance of cls
    '''

    return task(identifier, priority, description, cls)


def requires(*funcs):

    [ensure_callable(func) for func in funcs]

    def requires(fn):
        if not hasattr(fn, '__task_requires__'):
            fn.__task_requires__ = []
        fn.__task_requires__.extend(funcs)
        return fn

    return requires


def skips(*funcs):

    [ensure_callable(func) for func in funcs]

    def skips(fn):
        if not hasattr(fn, '__task_skips__'):
            fn.__task_skips__ = []
        fn.__task_skips__.extend(funcs)
        return fn

    return skips


def extract(func):

    ensure_callable(func)

    def extract(fn):
        fn.__task_extract__ = func
        return fn

    return extract


def pass_kwargs(keys_or_fn):
    if callable(keys_or_fn):
        fn = keys_or_fn
        fn.__task_extract__ = lambda ctx: ctx.kwargs
        return fn

    keys_or_fn = keys
    def pass_kwargs(fn):
        fn.__task_extract__ = lambda ctx: {k: ctx.kwargs[k] for k in keys}
        return fn


def inject(func):

    ensure_callable(func)

    def inject(fn):
        fn.__task_inject__ = func
        return fn

    return inject


def available(value):

    def available(fn):
        fn.__task_available__ = value
        return fn

    return available


def artifacts_key(key):

    def artifacts_key(ctx):
        '''Returns True when ctx.artifacts contains the key'''
        return key in ctx.artifacts

    return artifacts_key


def store_key(key):

    def store_key(ctx):
        '''Returns True when ctx.store contains the key'''
        return key in ctx.store

    return store_key


def kwargs_key(key):

    def kwargs_key(ctx):
        '''Returns True when key in ctx.kwargs'''
        return key in ctx.kwargs

    return kwargs_key


def task_success(identifier):

    def task_success(ctx):
        '''Returns True if the task has succeeded'''
        try:
            request = ctx.requests[identifier]
            return request.success
        except KeyError:
            return False

    return task_success


def task_done(identifier):

    def task_done(ctx):
        '''Returns True if the task is done'''
        try:
            request = ctx.requests[identifier]
            return request.done
        except KeyError:
            return False

    return task_success


def task_failed(identifier):

    def task_failed(ctx):
        '''Returns True if the task has succeeded'''
        try:
            request = ctx.requests[identifier]
            return request.failed
        except KeyError:
            return False

    return task_failed


# Utility Functions


def process_arguments(arguments):
    '''Process arguments returning args and kwargs.

    Acceptable arguments:
        tuple(tuple, dict) - args and kwargs
        tuple - just arguments
        dict(args=tuple, kwargs=dict) - dict with args and dict keys
        dict(**kwargs) - just a dict with keyword arguments
        dict(args=tuple, **kwrags) a dict with args and keyword arguments

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
        msg = [
            'Invalid return value signature:',
            f('Got: {arguments}'),
            'Expected:',
            '    (...)',
            '    {...}',
            '    ((...), {...})',
            '    {"args": (...), "kwargs": {...}}',
            '    {"args": (...), **kwargs}'
        ]
        raise ExtractorError('\n'.join(msg))
    return args, kwargs
