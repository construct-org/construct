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
    'pass_context',
    'pass_kwargs',
    'params',
    'available',
    'done',
    'failure',
    'success',
    'store',
    'artifact',
    'returns',
    'kwarg',
]

import threading
import time
import timeit
import sys
import inspect
from fstrings import f
from construct.constants import *
from construct.context import (
    _ctx_stack,
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

                try:
                    # Setup task
                    self.request.set_status(RUNNING)
                    self.request._before_task()

                    # Run task
                    result = self.request.task(
                        *self.request.args,
                        **self.request.kwargs
                    )

                    # Finish task
                    self.request.set_value(result)
                    self.request._after_task()
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

    def _before_task(self):
        if self.ctx is not None:
            self.args, self.kwargs = self.task.get_params(self.ctx)

    def _after_task(self):
        if self.ctx is not None:
            self.task.run_callbacks(self.ctx, self._value)

    def get(self, propagate=True):

        if self.success:
            return self._value

        if self.failed:
            if propagate:
                raise self._exc[0], self._exc[1], self._exc[2]
            return self._exc

        try:

            # Setup task
            self.set_status(RUNNING)
            self._before_task()
            self.push()

            # Run task
            result = self.task(*self.args, **self.kwargs)

            # Finish task
            self.set_value(result)
            self._after_task()
            return result

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
                 arg_getters=None, kwarg_getters=None, callbacks=None,
                 available=True):
        self.fn = fn
        if not isinstance(priority, Priority):
            priority = Priority(priority)
        self.priority = priority
        self.identifier = identifier
        self.description = description
        self.requires = requires or []
        self.skips = skips or []
        self.arg_getters = arg_getters or []
        self.kwarg_getters = kwarg_getters or {}
        self.callbacks = callbacks or []
        self._available = available

    def __repr__(self):
        return (
            'Task(identifier={}, fn={}, requires={})'
        ).format(
            repr(self.identifier),
            self.fn,
            self.requires,
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

    def get_params(self, ctx):

        args, kwargs = [], {}

        for getter in self.arg_getters:
            args.append(getter(ctx))

        for name, getter in self.kwarg_getters.items():
            if name == 'kwargs':
                more = getter(ctx)
                kwargs.update(more)
            else:
                kwargs[name] = getter(ctx)

        return tuple(args), kwargs

    def run_callbacks(self, ctx, result):

        for callback in self.callbacks:
            callback(ctx, result)

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

    def make_task(fn, identifier):
        return cls(
            fn,
            identifier=get_callable_name(fn),
            description=description or fn.__doc__,
            requires=pop_attr(fn, '__task_requires__', None),
            skips=pop_attr(fn, '__task_skips__', None),
            arg_getters=pop_attr(fn, '__task_arg_getters__', None),
            kwarg_getters=pop_attr(fn, '__task_kwarg_getters__', None),
            callbacks=pop_attr(fn, '__task_callbacks__', None),
            available=pop_attr(fn, '__task_available__', None),
            priority=priority if priority is not None else DEFAULT_PRIORITY
        )

    if callable(identifier):
        fn = identifier
        identifier = get_callable_name(fn)
        return make_task(fn, identifier)

    if isinstance(identifier, basestring) or identifier is None:
        def wrapper(fn):
            return make_task(fn, identifier)
        return wrapper

    raise TypeError("Argument must be: str or callable")


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


def pass_construct(fn):
    '''Task decorator that passes Construct object as first argument to task'''

    def pass_construct(ctx):
        return ctx.construct

    if not hasattr(fn, '__task_arg_getters'):
        fn.__task_arg_getters__ = []

    if len(fn.__task_arg_getters__):
        for getter in fn.__task_arg_getters__:
            if getattr(getter, '__name__', None) == 'pass_construct':
                return fn

    fn.__task_arg_getters__.insert(0, pass_construct)
    return fn


def pass_context(fn):
    '''Task decorator that passes Context object as first argument to task'''

    def pass_ctx(ctx):
        return ctx

    if not hasattr(fn, '__task_arg_getters__'):
        fn.__task_arg_getters__ = []

    if len(fn.__task_arg_getters__):
        for getter in fn.__task_arg_getters__:
            if getattr(getter, '__name__', None) == 'pass_ctx':
                return fn

    fn.__task_arg_getters__.insert(0, pass_ctx)
    return fn


def pass_kwargs(fn):
    '''Task decorator that passes all action kwargs to the task'''

    def pass_kwargs(ctx):
        return ctx.kwargs

    if not hasattr(fn, '__task_kwarg_getters__'):
        fn.__task_kwarg_getters__ = {}
    fn.__task_kwarg_getters__['kwargs'] = pass_kwargs
    return fn


def params(*args, **kwargs):
    '''Task decorator used to describe how to get args and kwargs to pass to
    the task. This should have the same signature as the task itself, but,
    each argument and keyword argument should be a function accepting one
    argument, ctx, that returns a value to pass to the task.

    Examples:

        >>> @task
        ... @params(store('a'), b=store('b'))
        ... def plus(a, b):
        ...     return a + b

        # pass_context provides ctx, so we describe the remaining args
        >>> @task
        ... @pass_context
        ... @params(store('a'), store('b'))
        ... def plus2(ctx, a, b):
        ...     value = a + b
        ...     ctx.store['plus_result'] = value
        ...     return value

    '''

    def to_getter(arg):
        if callable(arg):
            spec = inspect.getargspec(arg)
            if not spec.args or len(args) != 1:
                raise TypeError(
                    arg.__name__ +
                    ' must accept one argument: ctx'
                )
            return arg
        elif isinstance(arg, CtxAction):
            if not arg.gets:
                raise TypeError(
                    type(arg).__name__ +
                    ' can not be used as an argument to params()...'
                )
            return arg.get
        else:
            raise TypeError(
                'params received unsupported type: ' + type(cb).__name__
            )

    def describe_params(fn):
        if not hasattr(fn, '__task_arg_getters__'):
            fn.__task_arg_getters__ = []
        if not hasattr(fn, '__task_kwarg_getters__'):
            fn.__task_kwarg_getters__ = {}

        for arg in args:
            getter = to_getter(arg)
            fn.__task_arg_getters__.append(getter)

        for name, arg in kwargs.items():
            getter = to_getter(arg)
            fn.__task_kwarg_getters__[name] = getter

        return fn

    return describe_params


def returns(*callbacks):
    '''Add callbacks to run when the task successfully returns. Also accepts
    CtxAction objects like artifact(key), store(key), and kwarg(key).'''

    def returns(fn):
        fn.__task_callbacks__ = []

        for cb in callbacks:
            if callable(cb):
                spec = inspect.getargspec(cb)
                if spec.args and len(args) == 2:
                    fn.__task_callbacks__.append(cb)
                else:
                    return TypeError(
                        'Callback must accept two arguments: ctx and value'
                    )
            elif isinstance(cb, CtxAction):
                if not cb.sets:
                    raise TypeError(
                        type(cb).__name__ +
                        ' can not be used as an argument to returns()...'
                    )
                fn.__task_callbacks__.append(cb.set)
            else:
                raise TypeError(
                    'returns received unsupported type: ' + type(cb).__name__
                )
        return fn

    return returns


def available(value):
    '''Task available when value is True or value() is True'''

    def available(fn):
        fn.__task_available__ = value
        return fn

    return available


def success(identifier):
    '''Check if a task succeeded'''

    def success(ctx):
        '''Returns True if the task has succeeded'''
        try:
            request = ctx.requests[identifier]
            return request.success
        except KeyError:
            return False

    return success


def done(identifier):
    '''Check if a task is done'''

    def done(ctx):
        '''Returns True if the task is done'''
        try:
            request = ctx.requests[identifier]
            return request.done
        except KeyError:
            return False

    return task_success


def failure(identifier):
    '''Check if a task failed'''

    def failure(ctx):
        '''Returns True if the task has failed'''
        try:
            request = ctx.requests[identifier]
            return request.failed
        except KeyError:
            return False

    return failure


class CtxAction(object):

    section = ''
    sep = ':'
    actions = 'store', 'append', 'count'
    gets = True
    sets = True

    def __init__(self, key, action='store'):
        self.key = key
        self.action = action

    def split_key(self):
        if self.sep in self.key:
            keys = self.key.split()
            return keys[:-1], keys[-1]
        return [], self.key

    def get_section_key(self, ctx):
        keys, key = self.split_key()
        section = getattr(ctx, self.section)
        if keys:
            for key in keys:
                section = section.get(key)
        return section, key

    def get(self, ctx):
        section, key = self.get_section_key(ctx)
        return section[key]

    def set(self, ctx, value):
        section, key = self.get_section_key(ctx)
        if self.action == 'store':
            section[key] = value
        elif self.action == 'append':
            if key not in section:
                section[key] = []
            section[key].append(value)
        else:
            if key in section and type(section[key], (float, int)):
                section[key] += value


class artifact(CtxAction):
    '''Use as an argument for :func:`params` or :func:`returns`.
    When used with :func:`params`, artifact will get the value of the key
    from the context's "artifacts" dict and supply it as an arg or kwarg for
    the task. If used with :func:`returns`, artifact will inject the return
    value of the task into the specified key of the context's "artifacts" dict.
    You can specify a nested key using : as a separator.

    Examples:

        # Set ctx.artifacts['funky'] to return value of task
        >>> @task
        ... @returns(artifact('funky'))
        ... def funky_func():
        ...    return {}

        # Set ctx.artifacts['funky']['monkey'] to return value of task
        >>> @task
        ... @returns(artifact('funky:monkey'))
        ... def funky_monkey_func():
        ...    return 'Super Funky Monkey'
    '''
    section = 'artifacts'


class store(CtxAction):
    '''Use as an argument for :func:`params` or :func:`returns`.
    When used with :func:`params`, store will get the value of the key
    from the context's "store" dict and supply it as an arg or kwarg for
    the task. If used with :func:`returns`, store will inject the return
    value of the task into the specified key of the context's "store" dict.
    You can specify a nested key using : as a separator.

    Examples:

        # Pass ctx.store['x'] as an arg and ctx.store['y'] as kwarg to add
        # Set ctx.store['sum'] to the return value of add
        >>> @task
        ... @params(store('x'), b=store('y'))
        ... @returns(store('sum'))
        ... def add(a, b):
        ...    return a + b
    '''
    section = 'store'


class kwarg(CtxAction):
    '''Use as an argument for :func:`params`. When used with :func:`params`,
    kwarg will get the value of the key from the context's "kwargs" dict and
    supply it as an arg or kwarg for the task. This action can not be used with
    :func:`returns`.

    You can specify a nested key using : as a separator.

    Examples:

        # Pass ctx.store['x'] as an arg and ctx.store['y'] as kwarg to add
        # Set ctx.store['sum'] to the return value of add
        >>> @task
        ... @params(store('x'), b=store('y'))
        ... @returns(store('sum'))
        ... def add(a, b):
        ...    return a + b
    '''
    section = 'kwargs'

    def set(self, ctx, value):
        raise NotImplementedError('Can not use kwarg with the returns deco')

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
