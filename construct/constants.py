# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import sys
from .utils import unipath

PLATFORM = sys.platform.rstrip('1234567890')
if PLATFORM == 'darwin':
    PLATFORM = 'mac'

SETTINGS_FILE = 'construct.yaml'
USER_SETTINGS_FILE = unipath('~/.construct/construct.yaml')
USER_PATH = unipath('~/.construct')

DEFAULT_API_NAME = 'global'
DEFAULT_PATHS = [
    unipath('~/.construct'),
]
DEFAULT_LOCATION = 'local'
DEFAULT_MOUNT = 'projects'
DEFAULT_LOCATIONS = {
    'local': {
        'projects': unipath('~/projects').as_posix(),
        'lib': unipath('~/lib').as_posix()
    }
}
DEFAULT_TREE = {
    'folders': '',
    'asset': '{asset}',
    'asset_work': '{asset}/{task}/work/{host}',
    'asset_publish': '{asset}/{task}/publish/{ext}',
    'asset_reviews': '{asset}/{task}/review',
    'file': '{task}_{name}_v{version:0>3d}.{ext}',
    'sequence': '{task}_{name}_v{version:0>3}.{frame:0>4d}.{ext}',
}
DEFAULT_LOGGING = dict(
    version=1,
    formatters={'simple': {
        'format': '%(levelname).1s:%(name)s> %(message)s'
    }},
    handlers={
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        }
    },
    loggers={
        'construct': {
            'level': os.environ.get('CONSTRUCT_LOGGING_LEVEL', 'DEBUG'),
            'handlers': ['console'],
        }
    })
DEFAULT_SETTINGS = {
    'my_location': DEFAULT_LOCATION,
    'my_mount': DEFAULT_MOUNT,
    'locations': DEFAULT_LOCATIONS,
    'logging': DEFAULT_LOGGING,
}
DEFAULT_HOST = 'standalone'
