# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
from os.path import normpath
from glob import glob
from contextlib import contextmanager

from past.builtins import basestring

from .compat import Path


__all__ = [
    'import_file',
    'isolated_imports',
    'iter_modules',
    'unipath',
    'ensure_exists',
    'unload_modules',
    'get_lib_path',
    'update_env',
    'update_envvar',
]
this_package = Path(__file__).parent


def get_lib_path():
    return this_package.parent


def unipath(*paths):
    return Path(*paths).expanduser().resolve()


def ensure_exists(*folders):
    for folder in folders:
        try:
            os.makedirs(str(folder))
        except:
            pass


def update_env(d, **values):
    '''Updates an environment dict with the specified values. List values
    are combined with the existing values in d. String values override
    values in d.

    Example:
        >>> import os
        >>> env = os.environ.copy()
        >>> update_env(env, PATH=['some_path'], VAR='value')

    Arguments:
        d (dict): Environment dict to update
        **values: Values to update d with
    '''

    for k, v in values.items():
        update_envvar(d, k, v)


def update_envvar(d, k, v):
    '''Used by update_env to update a single key with the specified value.'''

    if isinstance(v, basestring):
        d[k] = v
    elif isinstance(v, list):
        v = os.pathsep.join(v)
        if k not in v:
            d[k] = v
        else:
            d[k] = os.pathsep.join([v, d[k]])
    else:
        d[k] = str(v)


@contextmanager
def isolated_imports(path=None, restore=True):
    '''Contextmanager that isolates all import'''

    old_path_cache = {k: v for k, v in sys.path_importer_cache.items()}
    old_modules = {k: v for k, v in sys.modules.items()}
    old_path = sys.path[:]

    try:

        if path:
            sys.path.insert(0, path)
        yield

    finally:

        sys.path[:] = old_path

        if restore:
            for k in list(sys.modules.keys()):
                if k in old_modules:
                    sys.modules[k] = old_modules[k]
                else:
                    del(sys.modules[k])

            for k in list(sys.path_importer_cache.keys()):
                if k in old_path_cache:
                    sys.path_importer_cache[k] = old_path_cache[k]
                else:
                    del(sys.path_importer_cache[k])


def unload_modules(*names):
    '''Removes modules and their children from sys.modules

    This is intended for use within the isolated_imports contextmanager.
    '''

    for name in names:
        for k in list(sys.modules.keys()):
            if k.startswith(name):
                del(sys.modules[k])


def import_file(path, isolated=True):
    '''Import python module by absolute path. The imported module is removed
    from sys.modules before being returned. This means the same module
    imported using import_file multiple times will return different module
    objects. I haven't decided on whether this is desirable for our use
    case yet, Extension loading. There have been no apparent downsides yet.
    '''

    path = Path(path)
    root = path.parent
    name = path.stem

    with isolated_imports(root, restore=isolated):
        unload_modules(name)
        mod = __import__(name, globals(), locals(), [])

    return mod


def iter_modules(*paths):
    '''Iterate over paths yielding all contained python modules and packages.

    The modules are removed from sys.modules after importing and before
    they are yielded.
    '''

    for path in paths:
        path = Path(path)
        for py_file in path.glob('*.py'):
            mod = import_file(py_file, isolated=False)
            yield mod

        for py_pkg in path.glob('*/__init__.py'):
            mod = import_file(py_pkg.parent, isolated=False)
            yield mod
