# -*- coding: utf-8 -*-
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

from cachetools import cached


__all__ = [
    'Api',
    'get_api',
    'set_api'
]

logging.config.dictConfig(DEFAULT_LOGGING)
_log = logging.getLogger(__name__)
_initialized = False


class Api(object):

    _apis = {}

    def __init__(self, name, **kwargs):
        self.name = name
        self.initialized = False
        self.path = Path()
        self.settings = Settings(self.path)
        self.extensions = Extensions(self)
        self.context = Context()
        self.schemas = schemas
        self.init()

    def init(self):

        _log.debug('Hi!')
        global _initialized
        if _initialized:
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

        _log.debug('Adding exit handler...')
        atexit.register(self.uninit)

        _initialized = True
        _log.debug('Done initializing.')


    def uninit(self):

        global _initialized
        if not _initialized:
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


@cached(cache=Api._apis)
def get_api(name=DEFAULT_API_NAME, **kwargs):
    return Api(name, **kwargs)


def set_api(api, name='global'):
    Api._apis[api.name] = api
