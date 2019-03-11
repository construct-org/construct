# -*- coding: utf-8 -*-
from __future__ import absolute_import
import atexit
import os
import yaml
import logging
import inspect
from copy import deepcopy
from functools import wraps
from logging.config import dictConfig

from .constants import (
    DEFAULT_HOST,
    DEFAULT_LOGGING,
    DEFAULT_PATHS,
    DEFAULT_API_NAME
)
from . import schemas
from .context import Context
from .settings import Settings
from .path import Path
from .extensions import (
    is_extension,
    is_extension_type,
    ExtensionManager,
)


__all__ = ['API']

logging.config.dictConfig(DEFAULT_LOGGING)
_log = logging.getLogger(__name__)
_cache = {}


def _on_exit():
    for api in list(_cache.values()):
        api.uninit()


atexit.register(_on_exit)


class API(object):

    def __init__(self, name=None, **kwargs):
        self.name = name
        self.initialized = False
        self.path = Path(kwargs.pop('path', None))
        self.settings = Settings(self.path)
        self.extensions = ExtensionManager(self)
        self.context = Context()
        self.schemas = schemas
        self._registered_members = {}
        self.init()

    def init(self):

        _log.debug('Hi!')
        if self.initialized:
            _log.error('Construct is already initialized...')
            return

        _log.debug('Setting up path...')
        self.path.load()

        _log.debug('Loading settings...')
        self.settings.load()

        _log.debug('Configuring logging...')
        dictConfig(self.settings.get('logging', DEFAULT_LOGGING))

        _log.debug('Loading extensions...')
        self.extensions.load()

        _log.debug('Loading context...')
        self.context.load()

        self.initialized = True
        _log.debug('Done initializing.')


    def uninit(self):

        if not self.initialized:
            _log.debug('Construct is not initialized...')
            return

        _log.debug('Clearing path...')
        self.path.unload()

        _log.debug('Unloading settings...')
        self.settings.unload()

        _log.debug('Clearing context...')
        self.context.unload()

        _log.debug('Unloading extensions...')
        self.extensions.unload()

        _cache.pop(self.name, None)
        _initialized = False
        _log.debug('Done uninitializing.')
        _log.debug('Goodbye!')

    def extend(self, name, obj):
        '''Register an obj with the API at the specified name. This provides
        a way for Extensions to register objects to be first-class members of
        the API.

        Example:
            def say(message):
                print(message)
            api.extend('say', say)
            api.say('Hello world!')
        '''

        if hasattr(self, name):
            raise NameError('API already has a member named "%s".' % name)

        if requires_wrapper(obj):
            obj = api_method_wrapper(self, obj)

        _log.debug('Adding %s to api.' % name)
        self._registered_members[name] = obj
        setattr(self, name, obj)

    def unextend(self, name):
        '''Unregister a name that was registered using extend.

        Example:
            api.unextend('say')
        '''

        if name in self._registered_members:
            _log.debug('Removing %s from api.' % name)
            self._registered_members.pop(name, None)
            self.__dict__.pop(name, None)
        else:
            _log.debug(name + ' was not registered with api.extend.')

    @property
    def host(self):
        '''Get the active Host Extension.'''
        return self.extensions.get(self.context.host, None)

    def get_mount(self, location=None, mount=None):
        '''Get a file system path to a mount.

        Arguments:
            location (str): Name of location. Defaults to 'my_location' setting
            mount (str): Name of mount. Defaults to 'my_mount' setting
        '''

        location = location or self.settings.get('my_location')
        mount = mount or self.settings.get('my_mount')
        return self.settings['locations'][location][mount]


def api_method_wrapper(api, fn):

    @wraps(fn)
    def api_method_call(*args, **kwargs):
        return fn(api, *args, **kwargs)

    return api_method_call


def requires_wrapper(obj):
    return callable(obj) and 'api' in inspect.getargspec(obj)[0]
