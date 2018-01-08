# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import os
import sys
from pkg_resources import iter_entry_points
from glob import iglob
from types import ModuleType
__all__ = ['import_mod', 'import_pkg', 'is_plugin', 'iter_plugins', 'discover']


def import_mod(path):
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


def import_pkg(path):
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


def is_plugin(obj):
    '''Check if obj is a valid construct plugin.'''

    plugin_methods = ['register', 'unregister', 'is_available']
    return all([hasattr(obj, method) for method in plugin_methods])


def iter_plugins(*paths):
    '''Iterate over paths yield plugin modules and packages'''

    for path in paths:
        for py_file in iglob(path + '/*.py'):
            mod = import_mod(py_file)
            if is_plugin(mod):
                yield mod.__name__, mod

        for py_pkg in iglob(path + '/*/__init__.py'):
            mod = import_pkg(os.path.dirname(py_pkg))
            if is_plugin(mod):
                yield mod.__name__, mod


def discover(*paths):
    '''Return a dict containing all construct plugins given the paths.'''

    plugins = {}

    for entry_point in iter_entry_points('construct'):
        name, obj = entry_point.name, entry_point.load()
        if is_plugin(obj):
            plugins[name] = obj

    for name, obj in iter_plugins(*paths):
        if name not in plugins:
            plugins[name] = obj

    return plugins
