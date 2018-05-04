# -*- coding: utf-8 -*-
from __future__ import absolute_import
import abc
import os
import inspect
import logging
from collections import defaultdict
from fnmatch import fnmatch

from construct.constants import EXTENSIONS_ENTRY_POINT
from construct.types import ABC
from construct.utils import iter_modules, ensure_type, missing, unipath
from construct.action import get_action_identifier, Action
from construct.compat import pkg_resources
pkg_resources = pkg_resources()


_extensions = {}
_log = logging.getLogger(__name__)


class Config(object):

    def __init__(self, key, default=missing):
        self.key = key
        self.default = default

    def __get__(self, obj, type=None):
        from construct.api import config

        if obj is None:
            return self
        if self.default is missing:
            return config[self.key]
        else:
            return config.get(self.key, self.default)


class Extension(ABC):

    name = None
    attr_name = None

    @abc.abstractproperty
    def name(self):
        '''Name of this extension like: "Builtins"'''

    @abc.abstractproperty
    def attr_name(self):
        '''Nice name used for attribute access like: "builtins"'''

    def __init__(self):
        self.enabled = True
        self._actions = {}
        self._tasks = defaultdict(list)
        self._template_paths = []
        self._forms = {}

    def _available(self, ctx=missing):
        if ctx is not missing:
            return self.available(ctx)
        return True

    def available(self, ctx):
        return True

    def _load(self):
        '''Load extension and call user implemented load'''
        self.load()

    def _unload(self):
        '''Unload extension and call user implemented unload'''
        self.unload()

    def load(self):
        '''Called by Construct when loading the extension.

        This method should register actions and tasks and perform any
        necessary setup.
        '''

    def unload(self):
        '''Called by Construct when unloading the extension.

        This method should unregister actions and tasks and perform any
        necessary teardown.
        '''

    def add_template_path(self, path):
        self._template_paths.append(unipath(path))

    def remove_template_path(self, path):
        p = unipath(path)
        if p in self._template_paths:
            self._template_paths.remove(p)

    def get_template_paths(self):
        return list(self._template_paths)

    def add_form(self, action_or_identifier, form):
        identifier = get_action_identifier(action_or_identifier)
        self._forms[identifier] = form

    def remove_form(self, action_or_identifier, form):
        identifier = get_action_identifier(action_or_identifier)
        if self._forms[identifier] == form:
            self._forms.pop(identifier)

    def get_form(self, action_or_identifier):
        identifier = get_action_identifier(action_or_identifier)
        return self._forms.get(identifier, None)

    def add_action(self, action):
        '''Add an action to this extension'''
        ensure_type(action, Action)

        if action.identifier not in self._actions:
            self._actions[action.identifier] = action

    def remove_action(self, action):
        '''Remove an action from this extensions'''
        ensure_type(action, Action)

        if action.identifier in self._actions:
            self._actions.pop(action.identifier)

    def get_actions(self, ctx=missing):
        '''Get all actions for the specified ctx'''

        if ctx is missing:
            return dict(self._actions)

        return {
            identifier: action
            for identifier, action in self._actions.items()
            if action._available(ctx)
        }

    def add_task(self, action_or_identifier, task, **task_overrides):
        '''Add a task to the specified action'''

        identifier = get_action_identifier(action_or_identifier)
        if task_overrides:
            task = task.clone(**task_overrides)
        self._tasks[identifier].append(task)

    def remove_task(self, action_or_identifier, task, **task_overrides):
        '''Remove a task from the specified action'''

        identifier = get_action_identifier(action_or_identifier)
        if task in self._tasks[identifier]:
            self._tasks.remove(task)

    def get_tasks(self, identifier, ctx=missing):
        '''Get all tasks for the spcified action '''

        all_tasks = list(self._tasks[identifier])

        for key, tasks in self._tasks.items():
            if key == identifier:
                continue
            if fnmatch(identifier, key):
                all_tasks.extend(tasks)

        if ctx is missing:
            return list(all_tasks)

        return [t for t in all_tasks if t.available(ctx)]


class HostExtension(Extension):

    name = 'Nice Name'
    host_name = 'name'

    def save_file(file):
        '''Save a file'''
        return NotImplemented

    def open_file(file):
        '''Open a file'''
        return NotImplemented

    def get_selection():
        '''Get the host's current selection'''
        return NotImplemented

    def set_selection(selection):
        '''Set the host's current selection'''
        return NotImplemented

    def get_workspace():
        '''Get the host's workspace'''
        return NotImplemented

    def set_workspace(directory):
        '''Set the host's workspace'''
        return NotImplemented

    def get_filepath():
        '''Get the path to the host's current file'''
        return NotImplemented

    def get_filename():
        '''Get the name of the host's current file'''
        return NotImplemented

    def get_frame_range():
        '''Get the frame range of the host'''
        return NotImplemented

    def set_frame_range(start_frame, end_frame):
        '''Set the frame range the host'''
        return NotImplemented

    def get_qt_parent(widget_cls=None):
        '''Get the host's main QT widget'''
        return NotImplemented

    def get_qt_loop(self):
        from Qt import QtWidgets
        return QtWidgets.QApplication.instance()


class ExtensionCollector(object):
    '''Handles Extension discovery and registration. Also allows looking
    up extensions via attribute access.'''

    def __init__(self):
        self.by_name = {}
        self.by_attr = {}

    def __getattr__(self, name):
        if name in self.by_name:
            return self.by_name[name]

        if name in self.by_attr:
            return self.by_attr[name]

        return self.__getattribute__(name)

    def __getitem__(self, name):
        return getattr(self, name)

    def __iter__(self):
        for ext in self.by_name.values():
            yield ext

    def collect(self):
        return dict(self.by_name)

    def register(self, extension):
        '''Register an extension'''

        if not is_extension_type(extension):
            raise RuntimeError('Not an extension: %s' % extension)

        if extension.name in _extensions:
            _log.debug('Extension already loaded: %s' % extension)
            return

        try:
            instance = extension()
            instance._load()
        except Exception as e:
            _log.debug(
                'Failed to load extension: %s: %s' % (extension, e.message)
            )
            return

        self.by_name[extension.name] = instance
        self.by_attr[extension.attr_name] = instance
        _log.debug('Registered extension: %s', extension)

    def unregister(self, extension):
        '''Unregister an extension'''

        if not is_extension_type(extension):
            raise RuntimeError('Not an extension: %s' % extension)

        registered_extension = self.by_name.get(extension.name, None)
        is_same_extension = (
            registered_extension is extension or
            isinstance(registered_extension, extension) or
            registered_extension.name == extension.name
        )
        if is_same_extension:
            self.by_name.pop(extension.name)
            self.by_attr.pop(extension.attr_name)
            registered_extension._unload()
            _log.debug('Unregistered extension: %s', registered_extension)

    def clear(self):
        '''Unloads and deletes all extensions'''

        while self.by_name:
            name, ext = self.by_name.popitem()
            ext.unload()
            _log.debug('Unregistered extension: %s' % ext)
            del ext

        self.by_attr = {}

    def discover(self, *paths):
        '''Discover extensions

            1. Search construct.extensions entry_point
            2. Search paths passed to discover_extensions
            3. Search configuration EXTENSION_PATHS
            4. Search CONSTRUCT_EXTENSION_PATHS environment variable
        '''

        from construct.api import config

        search_paths = list(paths)

        entry_points = pkg_resources.iter_entry_points(EXTENSIONS_ENTRY_POINT)
        for entry_point in entry_points:
            obj = entry_point.load()
            for _, extension in inspect.getmembers(obj, is_extension_type):
                self.register(extension)

        cfg_search_paths = config.get('EXTENSION_PATHS', [])
        search_paths.extend(cfg_search_paths)

        env_search_paths = os.environ.get('CONSTRUCT_EXTENSION_PATHS')
        if env_search_paths:
            search_paths.extend(env_search_paths.split(os.pathsep))

        for mod in iter_modules(*search_paths):
            for _, extension in inspect.getmembers(mod, is_extension_type):
                self.register(extension)


EXTENSION_TYPES = (Extension, HostExtension)


def is_extension_type(obj):
    return (
        obj not in EXTENSION_TYPES and
        isinstance(obj, type) and
        issubclass(obj, EXTENSION_TYPES)
    )


def is_extension(obj):
    return isinstance(obj, EXTENSION_TYPES)
