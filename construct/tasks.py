# -*- coding: utf-8 -*-
from __future__ import absolute_import

__all__ = [
    'RequestThread',
    'AsyncRequest',
    'AsyncTask',
    'Request',
    'Task',
    'TaskCollection',
    'task',
    'async_task',
    'sort_tasks',
    'group_tasks',
    'requires',
    'skips',
    'pass_context',
    'pass_args',
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
import sys
import inspect
import logging
import six
from operator import attrgetter
from collections import OrderedDict
from construct.compat import basestring
from construct.constants import *
from construct.context import _ctx_stack, _req_stack
from construct.utils import (
    get_callable_name,
    pop_attr,
    ensure_callable,
)
from construct.types import Priority
from construct.errors import TimeoutError, TaskError
from construct import signals


_log = logging.getLogger(__name__)
DEFAULT_PRIORITY = Priority(0)


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
            if propagate:
                six.reraise(*self.request._exc)
            return self.request._exc

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
        self.push()
        self.set_status(WAITING)
        self.pop()

    def push(self):
        if _ctx_stack.top is not self.ctx:
            _ctx_stack.push(self.ctx)
        if _req_stack.top is not self:
            _req_stack.push(self)

    def pop(self):
        if _req_stack.top is self:
            _req_stack.pop()
        if _ctx_stack.top is self.ctx:
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

        self.push()
        try:
            last_status = status
            self._status = status
            signals.send('request.status.changed', self, last_status, status)
        finally:
            self.pop()

    @property
    def enabled(self):
        return self._enabled

    def set_enabled(self, value):
        self._enabled = value
        signals.send('request.enabled', self, self._enabled)

    @property
    def success(self):
        return self._status == SUCCESS

    @property
    def failed(self):
        return self._status == FAILED

    @property
    def done(self):
        return self._status in DONE_STATUSES

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
                six.reraise(*self._exc)
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
            self.set_exception(*exc_info)
            if propagate:
                six.reraise(*exc_info)
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

    request_cls = Request

    def __init__(self, fn, identifier=None, description=None,
                 priority=DEFAULT_PRIORITY, requires=None, skips=None,
                 arg_getters=None, kwarg_getters=None, callbacks=None,
                 available=True, parent=None):
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
        self.parent = parent

    def __call__(self, *args, **kwargs):
        if self.bound_method:
            return self.fn(self.parent, *args, **kwargs)
        else:
            return self.fn(*args, **kwargs)

    def __repr__(self):
        return '<{} {} at 0x{}>(identifier={!r})'.format(
            ('unbound', 'bound')[self.bound],
            self.__class__.__name__,
            id(self),
            self.identifier
        )

    def __get__(self, obj, type):
        if obj is None:
            return self

        bind_task = self.clone(parent=obj)

        for name, member in inspect.getmembers(type):
            if member is self:
                setattr(obj, name, bind_task)

        return bind_task

    @property
    def bound(self):
        return self.parent is not None

    @property
    def bound_method(self):
        spec = inspect.getargspec(self.fn)
        return self.bound and 'self' in spec.args

    @property
    def func_name(self):
        return get_callable_name(self.fn)

    def clone(self, **kwargs):
        '''Create a new Task instance, overriding any kwargs you need to'''

        kwargs.setdefault('fn', self.fn)
        kwargs.setdefault('identifier', self.identifier)
        kwargs.setdefault('description', self.description)
        kwargs.setdefault('priority', self.priority)
        kwargs.setdefault('requires', self.requires)
        kwargs.setdefault('skips', self.skips)
        kwargs.setdefault('arg_getters', self.arg_getters)
        kwargs.setdefault('kwarg_getters', self.kwarg_getters)
        kwargs.setdefault('callbacks', self.callbacks)
        kwargs.setdefault('available', self._available)
        kwargs.setdefault('parent', self.parent)
        return self.__class__(**kwargs)

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
        return self.request_cls(self, ctx, args, kwargs)


class AsyncTask(Task):

    request_cls = AsyncRequest


class TaskCollection(object):

    identifier = None

    def __init__(self, identifier=None, tasks=None):
        self.identifier = identifier or self.identifier
        self.tasks = []

        # Bind tasks
        if tasks:
            if isinstance(tasks, (list, tuple, set, self.__class__)):
                for task in tasks:
                    self._bind_task(task)
            else:
                raise ValueError('Tasks must be a list of task objects')

        # Bind classmethod tasks
        for name, member in inspect.getmembers(self.__class__):
            if isinstance(member, Task):
                bound_task = getattr(self, name)
                self.tasks.append(bound_task)

    def __iter__(self):
        return iter(self.tasks)

    def __len__(self):
        return len(self.tasks)

    def __getitem__(self, index):
        return self.tasks.__getitem__(index)

    def __contains__(self, task):
        if task in self.tasks:
            return True

        for t in self.tasks:
            if t.identifier == task.identifier:
                return True

        return False

    def index(self, task):
        for i, bound_task in enumerate(self.tasks):
            if bound_task.identifier == task.identifier:
                return i
        raise ValueError('%s is not in TaskCollection' % task.identifier)

    def sort(self):
        '''Sort tasks by priority'''

        self.tasks.sort(key=lambda t: t.priority)

    def _bind_task(self, task):
        '''Bind and add task to this collection'''

        if task in self:
            return

        bind_name = task.func_name
        if hasattr(self, bind_name):
            raise NameError(
                'TaskCollection already has a method %s' % bind_name
            )

        if task.parent is not self:
            task = task.clone(parent=self)
            setattr(self, bind_name, task)

        self.tasks.append(task)

    def _unbind_task(self, task):
        '''Unbind and remove a task from this collection'''

        try:
            index = self.index(task)
            task = self.tasks.pop(index)
            bind_name = task.func_name
            if getattr(self, bind_name, None) is task:
                delattr(self, bind_name)
        except ValueError:
            pass

    def append(self, task):
        '''Bind and add a task to this collection'''

        self._bind_task(task)

    def remove(self, task):
        '''Remove a task from this collection'''

        self._unbind_task(task)

    def extend(self, tasks):
        '''Bind and add a list of tasks to this collection'''

        for task in tasks:
            self._bind_task(task)


# Decorator interface


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
            identifier=identifier or get_callable_name(fn),
            description=description or fn.__doc__,
            requires=pop_attr(fn, '__task_requires__', None),
            skips=pop_attr(fn, '__task_skips__', None),
            arg_getters=pop_attr(fn, '__task_arg_getters__', None),
            kwarg_getters=pop_attr(fn, '__task_kwarg_getters__', None),
            callbacks=pop_attr(fn, '__task_callbacks__', None),
            available=pop_attr(fn, '__task_available__', True),
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
    '''Task decorator describing a tasks's requirements.

    Each requirement must be a callable accepting ctx as an argument. Once all
    requirements are met, the task is ready to run. The ActionRunner will move
    the task from the waiting queue to the ready queue and execute it in the
    next loop.

    Require the success of another task:
        >>> @task
        ... @requires(success('other.task'))
        ... def my_task():
        ...     pass

    Require failure of another task:
        >>> @task
        ... @requires(failure('other.task'))
        ... def my_task():
        ...     pass
    '''

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


def pass_args(fn):
    '''Task decorator that passes Context object as first argument to task'''

    def pass_args(ctx):
        return ctx.args

    if not hasattr(fn, '__task_arg_getters__'):
        fn.__task_arg_getters__ = []

    if len(fn.__task_arg_getters__):
        for getter in fn.__task_arg_getters__:
            if getattr(getter, '__name__', None) == 'pass_args':
                return fn

    fn.__task_arg_getters__.insert(0, pass_args)
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
                'params received unsupported type: ' + type(arg).__name__
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
    '''Task decorator that adds callbacks to run when the task successfully
    returns. Also accepts CtxAction objects like artifact(key) and store(key)
    '''

    def returns(fn):
        if not hasattr(fn, '__task_callbacks__'):
            fn.__task_callbacks__ = []

        for callback in callbacks:
            if callable(callback):
                spec = inspect.getargspec(callback)
                if spec.args and len(spec.args) == 2:
                    fn.__task_callbacks__.append(callback)
                else:
                    return TypeError(
                        'Callback must accept two arguments: ctx and value'
                    )
            elif isinstance(callback, CtxAction):
                if not callback.sets:
                    raise TypeError(
                        type(callback).__name__ +
                        ' can not be used as an argument to returns()...'
                    )
                fn.__task_callbacks__.append(callback.set)
            else:
                raise TypeError(
                    'returns received unsupported type: ' +
                    type(callback).__name__
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
            raise TaskError('success(%r): Request not found..' % identifier)

    return success


def done(identifier):
    '''Check if a task is done'''

    def done(ctx):
        '''Returns True if the task is done'''
        try:
            request = ctx.requests[identifier]
            return request.done
        except KeyError:
            raise TaskError('done(%r): Request not found..' % identifier)

    return done


def failure(identifier):
    '''Check if a task failed'''

    def failure(ctx):
        '''Returns True if the task has failed'''
        try:
            request = ctx.requests[identifier]
            return request.failed
        except KeyError:
            raise TaskError('failure(%r): Request not found..' % identifier)

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


# Sort methods

def sort_tasks(tasks):
    '''Sort the given tasks by priority'''

    return sorted(tasks, key=attrgetter('priority'))


def group_tasks(tasks):
    '''Group sorted tasks by priority'''

    groups = OrderedDict()
    for task in tasks:
        groups.setdefault(task.priority, [])
        groups[task.priority].append(task)
    return groups
