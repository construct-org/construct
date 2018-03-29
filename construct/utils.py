# -*- coding: utf-8 -*-
from __future__ import absolute_import

__all__ = [
    'ensure_callable',
    'ensure_instance',
    'ensure_type',
    'env_with_default',
    'get_qualname',
    'get_callable_name',
    'path_split',
    'pop_attr',
    'update_dict',
    'unipath',
    'package_path',
    'import_file',
    'iter_modules',
    'missing',
]

import inspect
import os
import sys
from collections import Mapping
from fstrings import f
from glob import glob
from contextlib import contextmanager
from construct.compat import basestring


platform = sys.platform.rstrip('0123456789').lower()
if platform == 'darwin':
    platform = 'mac'
missing = object()


def package_path(*paths):
    '''Return a path relative to the construct package'''

    return unipath(os.path.dirname(__file__), *paths)


def unipath(*paths):
    '''os.path.join with forward slashes only.'''

    return os.path.abspath(os.path.join(*paths).replace('\\', '/'))


def get_qualname(obj):
    '''Get the qualified name (dotted path) of the object'''

    try:
        return obj.__qualname__
    except AttributeError:
        pass

    if inspect.ismethod(obj):
        if obj.__self__:
            cls = obj.__self__.__class__
        else:
            cls = obj.im_class
        return cls.__name__ + '.' + obj.__name__

    return get_callable_name(obj)


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


@contextmanager
def temp_syspath(path, *old_module_names):

    old_modules = [(n, sys.modules.pop(n, None)) for n in old_module_names]
    old_path = sys.path[:]
    sys.path.insert(0, path)
    try:
        yield
    finally:
        sys.path[:] = old_path
        for k, v in old_modules:
            sys.modules[k] = v


def import_file(path):
    '''Import python module by absolute path. The imported module is removed
    from sys.modules before being returned. This means the same module
    imported using import_file multiple times will return different module
    objects. I haven't decided on whether this is desirable for our use
    case yet, Extension loading. There have been no apparent downsides yet.
    '''

    root, basename = os.path.split(path)
    name, _ = os.path.splitext(basename)

    with temp_syspath(root, name):
        mod = __import__(name, globals(), locals(), [], -1)
        sys.modules.pop(name)

    return mod


def iter_modules(*paths):
    '''Iterate over paths yielding all contained python modules and packages.

    The modules are removed from sys.modules after importing and before
    they are yielded.
    '''

    for path in paths:
        for py_file in glob(path + '/*.py'):
            mod = import_file(py_file)
            yield mod

        for py_pkg in glob(path + '/*/__init__.py'):
            mod = import_file(os.path.dirname(py_pkg))
            yield mod
