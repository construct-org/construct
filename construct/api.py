# -*- coding: utf-8 -*-
from __future__ import absolute_import
import atexit
import os
import yaml
import logging
from copy import deepcopy
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
    Extensions,
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
        self.extensions = Extensions(self)
        self.context = Context()
        self.schemas = schemas
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

    def get_host(self):
        host_name = os.environ.get('CONSTRUCT_HOST', DEFAULT_HOST)
        return self.extensions.get(host_name, None)

    def set_host(self, host_name_or_extension):
        if is_extension(host_name_or_extension):
            os.environ['CONSTRUCT_HOST'] = host_name_or_extension.name
        else:
            os.environ['CONSTRUCT_HOST'] = host_name_or_extension

    def get_mount(self, location=None, mount=None):
        location = location or self.settings.get('my_location')
        mount = mount or self.settings.get('my_mount')
        return self.settings['locations'][location][mount]
