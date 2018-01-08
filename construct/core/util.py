# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import
import os
from fstrings import f
from construct.compat import basestring
__all__ = [
    'ensure_callable',
    'ensure_instance',
    'ensure_type',
    'env_with_default',
    'get_callable_name',
    'path_split',
]


def get_callable_name(obj):
    '''Get name of obj object or callable'''
    try:
        return obj.func_name
    except NameError:
        return obj.__name__
    except NameError:
        return obj.__class__.__name__
    except NameError:
        return obj.__func__.__name__


def path_split(value):

    if isinstance(value, basestring):
        return [value]
    elif ';' in value or ':' in value:
        return value.split(os.pathsep)

    raise EnvironmentError('Can not split: ' + value)


def env_with_default(var, default, converter=None):
    '''Get an environment variable or a default value.'''

    if var in os.environ:
        value = os.environ[var]
    else:
        value = default

    if converter:
        value = converter(value)

    return value


def ensure_type(obj, type_, exc_type=TypeError):
    if not issubclass(obj, type_):
        raise exc_type(f('{obj} must be subclass of {type_}'))


def ensure_instance(obj, type_, exc_type=TypeError):
    if not isinstance(obj, type_):
        raise exc_type(f('{obj} must be instance of {type_}'))


def ensure_callable(obj, exc_type=TypeError):
    '''Ensures that an obj is callable'''

    if not callable(obj):
        raise exc_type('{obj} must be callable')
