# -*- coding: utf-8 -*-
from __future__ import absolute_import

__all__ = [
    'ensure_callable',
    'ensure_instance',
    'ensure_type',
    'env_with_default',
    'get_callable_name',
    'path_split',
    'pop_attr',
    'update_dict',
    'unipath',
    'package_path',
    'import_module',
    'import_package',
    'iter_modules',
    'missing',
]

import sys
import os
from collections import Mapping
from glob import glob
from types import ModuleType
from fstrings import f
from construct.compat import basestring


platform = sys.platform.rstrip('0123456789').lower()
if platform == 'darwin':
    platform = 'mac'
missing = object()


def package_path(*paths):
    '''Return a path relative to the construct package'''

    return os.path.join(os.path.dirname(__file__), *paths)


def unipath(*paths):
    '''os.path.join with forward slashes only.'''

    return os.path.abspath(os.path.join(*paths).replace('\\', '/'))


def pop_attr(obj, attr, default):
    '''Get the value of an attr then delete it else return default'''

    try:
        value = getattr(obj, attr)
        delattr(obj, attr)
    except AttributeError:
        value = default
    return value


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


def update_dict(d, u):
    '''Update a dict recursively.

    See also:
        https://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
    '''

    for k, v in u.items():
        if isinstance(v, Mapping):
            dv = d.get(k, {})
            if isinstance(dv, Mapping):
                d[k] = update_dict(dv, v)
            else:
                d[k] = v
        else:
            d[k] = v
    return d


def import_module(path):
    '''Import python module by absolute path'''

    dirname, basename = os.path.split(path)
    name, _ = os.path.splitext(basename)

    # Compile module
    mod = ModuleType(name)
    mod.__name__ = name
    mod.__file__ = path
    with open(path, 'r') as f:
        src = f.read()
    code = compile(src, '', 'exec')
    exec(code, mod.__dict__)

    return mod


def import_package(path):
    '''Import python package by absolute path'''

    root, basename = os.path.split(path)
    name, _ = os.path.splitext(basename)
    root = os.path.dirname(path)

    sys_path = list(sys.path)
    sys.path.insert(0, root)
    mod = __import__(name, globals(), locals(), [], -1)
    sys.path[:] = sys_path
    sys.modules.pop(name)

    return mod


def iter_modules(*paths):
    '''Iterate over paths yielding python modules and packages'''

    for path in paths:
        for py_file in glob(path + '/*.py'):
            mod = import_module(py_file)
            yield mod

        for py_pkg in glob(path + '/*/__init__.py'):
            mod = import_package(os.path.dirname(py_pkg))
            yield mod
