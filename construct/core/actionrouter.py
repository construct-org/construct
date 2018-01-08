# -*- coding: utf-8 -*-
from __future__ import absolute_import
import functools
from fstrings import f
from construct.core.util import ensure_callable
from construct.err import ExtractorError
__all__ = ['action_router']


def action_router(function, extractor=None, injector=None):
    '''Wrap a function allowing it to be used as an action subscriber. Provide
    a standard function, and an extractor that takes a :class:`Action`
    instance as an argument and returns keyword arguments for your function.
    If you provide an injector, the injector function will be passed the action
    and the return value of the function. Usually the injector will place the
    return value of the function in the :attr:`Action.data` dict.

    Examples:

        def add(a, b):
            return a + b

        add_router = action_router(
            add,
            lambda action: {'a': action.kwargs['a'], 'b': action.kwargs['b']},
            lambda action, result: action.data.update(add_result=result)
        )

        cons.action_hub.subscribe(add_router, priority=0)

    Arguments:
        function (callable): Object to wrap and forward arguments to
        extractor (callable): Callable that returns arguments to send to
            function
        injector (callable): Callable that injects return value of function
            into action.

    Returns:
        Callable: Takes argument *action*. Use with :meth:`ActionHub.subscribe`
    '''

    ensure_callable(function)
    ensure_callable(extractor)
    if injector:
        ensure_callable(injector)

    @functools.wraps(function)
    def do_action(action):

        # Extract arguments from action
        if extractor:
            arguments = extractor(action)
            args, kwargs = process_arguments(arguments)
        else:
            args, kwargs = (), {}

        # Run wrapped function
        result = function(*args, **kwargs)

        # Inject return value of function into action
        if injector:
            injector(action, result)

        return result

    return do_action


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
