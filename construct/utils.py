# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import sys
from os.path import abspath, expanduser, join as joinpath
from contextlib import contextmanager
from glob import glob

from past.builtins import basestring

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
this_package = os.path.dirname(__file__)


def get_lib_path():
    return os.path.dirname(this_package).replace('\\', '/')


def unipath(*paths):
    return abspath(expanduser(joinpath(*paths))).replace('\\', '/')


def ensure_exists(*folders):
    for folder in folders:
        if not os.path.isdir(folder):
            os.makedirs(folder)


def update_env(d, **values):
    '''Updates an environment dict with the specified values.'''

    for k, v in values.items():
        update_value(d, k, v)


def update_envvar(d, k, v):
    '''Update one value in an environment dict.'''

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
        for k, v in list(sys.modules.items()):
            if k.startswith(name):
                del(sys.modules[k])


def import_file(path, isolated=True):
    '''Import python module by absolute path. The imported module is removed
    from sys.modules before being returned. This means the same module
    imported using import_file multiple times will return different module
    objects. I haven't decided on whether this is desirable for our use
    case yet, Extension loading. There have been no apparent downsides yet.
    '''

    root, basename = os.path.split(path)
    name, _ = os.path.splitext(basename)

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
        for py_file in glob(path + '/*.py'):
            mod = import_file(py_file, isolated=False)
            yield mod

        for py_pkg in glob(path + '/*/__init__.py'):
            mod = import_file(os.path.dirname(py_pkg), isolated=False)
            yield mod
