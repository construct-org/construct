import os
import timeit
import time
from construct.utils import package_path


WAITING = 'WAITING'
PENDING = 'PENDING'
RUNNING = 'RUNNING'
SUCCESS = 'SUCCESS'
FAILED = 'FAILED'
SKIPPED = 'SKIPPED'
PAUSED = 'PAUSED'
DISABLED = 'DISABLED'
ENABLED = 'ENABLED'
DONE_STATUSES = [SUCCESS, FAILED]
ACTION_SIGNALS = [
    'action.*',
    'group.*',
    'request.*',
]


EXTENSIONS_ENTRY_POINT = 'construct.extensions'
USER_CONFIG = os.path.expanduser('~/.construct/construct.yaml')
DEFAULT_CONFIG = package_path('defaults', 'construct.yaml')
DEFAULT_ROOT = os.path.expanduser('~/projects')
DEFAULT_HOST = 'standalone'
DEFAULT_LOGGING = dict(
    version=1,
    formatters={
        'simple': {
            'format': '%(levelname).1s:%(name)s> %(message)s'
        }
    },
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
    }
)

FSFS_DATA_ROOT = '.data'
FSFS_DATA_FILE = 'data'

TIMER = timeit.default_timer
SLEEP = time.sleep
