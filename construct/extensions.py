# -*- coding: utf-8 -*-
import logging
import inspect

from . import schemas
from .utils import iter_modules, unipath

__all__ = [
    'Action',
    'Extension',
    'Setting',
    'Extensions',
    'Host',
    'is_extension',
    'is_extension_type',
]


missing = object()
_log = logging.getLogger(__name__)


class Extension(object):

    identifier = ''
    label = ''
    icon = ''

    def __init__(self, api):
        self.api = api
        self.settings = api.settings

    def load(self, api):
        '''Called by Construct when loading the extension.

        This method should register actions and tasks and perform any
        necessary setup.
        '''

    def unload(self, api):
        '''Called by Construct when unloading the extension.

        This method should unregister actions and tasks and perform any
        necessary teardown.
        '''

    def is_available(self, ctx):
        '''Return True if the Action is available in the given context'''
        return True

    def get_actions(self, ctx):
        '''Called by Construct when finding actions for a specific context.'''
        return []


class Setting(object):
    '''Provides easy access to a key in the current Apis settings.

    Examples:
        class MyExtension(Extension):
            software = Setting('software')
    '''

    def __init__(self, key):
        self.key = key

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        return obj.settings[self.key]


class Action(Extension):

    def __call__(self, *args, **kwargs):
        ctx = kwargs.pop('ctx', self.api.context.copy())
        ctx['args'] = args
        ctx['kwargs'] = kwargs
        ctx['interface'] = self.interface(ctx)

        # TODO: validate args and kwargs
        # use inspect.getargspec to map args to names
        # v = schemas.new_validator(ctx['interface'])
        # kwargs = v.validated(...)
        # self.run(**kwargs)

        self.run(*args, **kwargs)

    def interface(self, ctx):
        '''Return a list or dict describing the args this Action accepts.'''
        return {}

    def run(self, *args, **kwargs):
        '''The main method of this action.'''
        return NotImplemented


class Host(Extension):

    def modified(self):
        '''Check if current file is modified'''
        return NotImplemented

    def save_file(self, file):
        '''Save a file'''
        return NotImplemented

    def open_file(self, file):
        '''Open a file'''
        return NotImplemented

    def get_selection(self):
        '''Get the host's current selection'''
        return NotImplemented

    def set_selection(self, selection):
        '''Set the host's current selection'''
        return NotImplemented

    def get_workspace(self):
        '''Get the host's workspace'''
        return NotImplemented

    def set_workspace(self, directory):
        '''Set the host's workspace'''
        return NotImplemented

    def get_filepath(self):
        '''Get the path to the host's current file'''
        return NotImplemented

    def get_filename(self):
        '''Get the name of the host's current file'''
        return NotImplemented

    def get_frame_rate(self):
        '''Get the frame rate of the host
        Returns:
            float - fps
        '''
        return NotImplemented

    def set_frame_rate(self, fps):
        '''Set the frame rate of the host
        Arguments:
            fps (float) - Frames per second
        '''
        return NotImplemented

    def get_frame_range(self):
        '''Get the frame range of the host
        Returns:
            [min_frame, start_frame, end_frame, max_frame]
        '''
        return NotImplemented

    def set_frame_range(self, min, start, end, max):
        '''Set the frame range of the host
        Arguments:
            min_frame (int): Min frame of timeline
            start_frame (int): Start frame of animation
            end_frame (int): End frame of animation
            max_frame (int): Max frame of timeline
        '''
        return NotImplemented

    def get_qt_parent(self):
        '''Get the host's main QT widget'''
        return NotImplemented

    def get_qt_app(self):
        from Qt import QtWidgets
        return QtWidgets.QApplication.instance()


EXTENSION_TYPES = (Extension, Host, Action)


def is_extension_type(obj):
    '''Check if an obj is an Extension type.'''

    return (
        obj not in EXTENSION_TYPES and
        isinstance(obj, type) and
        issubclass(obj, EXTENSION_TYPES)
    )


def is_extension(obj):
    '''Check if an obj is an Extension instance.'''

    return isinstance(obj, EXTENSION_TYPES)


class Extensions(dict):

    def __init__(self, api):
        self.api = api
        self.path = self.api.path
        self.settings = self.api.settings

    def load(self):
        '''Discover and load all Extensions'''

        for ext in self.discover():
            self.register(ext)

    def unload(self):
        '''Unload all Extensions'''

        for ext in self.values():
            _log.debug('Unloading extension: %s' % ext)
            ext.unload(self.api)

        self.clear()

    def register(self, ext):
        '''Register an Extension'''

        if self.loaded(ext):
            _log.debug('Extension already loaded: %s' % ext)

        # Initialize extension
        _log.debug('Loading extension: %s' % ext)
        if is_extension_type(ext):
            inst = ext(self.api)
        elif is_extension(ext):
            inst = ext
        else:
            _log.error('Expected Extension type got %s' % ext)
            return

        # Load extension
        try:
            inst.load(self.api)
            self[ext.identifier] = inst
        except:
            _log.exception("Failed to load extension: %s" % ext)

    def unregister(self, ext):
        '''Unregister an Extension'''

        identifier = getattr(ext, 'identifier', ext)
        inst = self.pop(identifier, None)
        _log.debug('Unloading extension: %s' % ext)
        inst.unload(self.api)

    def loaded(self, ext):
        '''Check if an Extension has been loaded.'''

        identifier = getattr(ext, 'identifer', ext)
        return identifier in self

    def discover(self):
        '''Find and iterate over all Extension subclasses

        1. Yields Builtin Extensions
        2. Yields Extensions in python files in CONSTRUCT_PATH
        3. Yields Extensions in settings['extensions']
        '''

        from . import builtins
        for ext in builtins.extensions:
            yield ext

        ext_paths = [unipath(p, 'extensions') for p in self.path]
        for mod in iter_modules(*ext_paths):
            for _, ext in inspect.getmembers(mod, is_extension_type):
                yield ext

        for module_path in self.settings.get('extensions', []):
            try:
                mod = __import__(module_path)
            except ImportError:
                _log.debug('Extension module does not exist: ' + module_path)
            for _, ext in inspect.getmembers(mod, is_extension_type):
                yield ext

    def ls(self, typ=None):
        '''Get a list of available extensions.

        Arguments:
            typ (Extension, Optional): List only a specific type of Extension.

        Examples:
            ls()  # lists all extensions
            ls(Host)  # list only Host extensions
        '''

        matches = []
        for ext in self.values():
            if not type or isinstance(ext, typ):
                matches.append(ext)
        return matches

    def get_available(self, ctx=None):
        '''Get extensions available in the provided context.'''

        ctx = ctx or self.api.context.copy()
        return [ext for ext in self.values() if ext.is_available(ctx)]

    def get_actions(self, ctx=None):
        '''Get actions available in the provided context.'''

        ctx = ctx or self.api.context.copy()
        actions = {}
        for ext in self.get_available(ctx):

            # Get normally registered Actions
            if isinstance(ext, Action):
                if ext.identifier not in actions:
                    actions[ext.identifier] = ext

            # Get dynamically generated actions
            # from available Extensions
            for action in ext.get_actions(ctx):
                action = action()
                if action.identifier not in actions:
                    action.load()
                    actions[action.identifier] = action

        return actions
