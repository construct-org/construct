# -*- coding: utf-8 -*-

from __future__ import absolute_import

# Standard library imports
import copy
import getpass
import json
import os

# Local imports
from .compat import basestring
from .constants import DEFAULT_HOST, PLATFORM


__all__ = ['Context']


def encode(obj):
    '''Encode objects to stuff in environment variables'''

    return json.dumps(obj)


def decode(obj):
    '''Decode objects stored in environment variables'''

    return json.loads(obj)


class Context(dict):
    '''Represents a state used to interact with Construct. The Construct object
    provides both item and attribute access.

    >>> ctx = Context()
    >>> ctx.project = {'name': 'my_project'}
    >>> ctx['project'] == ctx.project

    Context objects can be loaded from and stored in environment variables
    prefixed with **CONSTRUCT_**.

    +-----------+------------------------------------------------------+
    |   key     |                     description                      |
    +===========+======================================================+
    | user      | usually the same as the logged in user               |
    +-----------+------------------------------------------------------+
    | platform  | Current platform [win, linux, mac]                   |
    +-----------+------------------------------------------------------+
    | host      | Host application like maya, nuke, standalone, etc... |
    +-----------+------------------------------------------------------+
    | location  | Location name                                        |
    +-----------+------------------------------------------------------+
    | mount     | Mount name                                           |
    +-----------+------------------------------------------------------+
    | project   | Project name                                         |
    +-----------+------------------------------------------------------+
    | bin       | Bin name                                             |
    +-----------+------------------------------------------------------+
    | asset     | Asset name                                           |
    +-----------+------------------------------------------------------+
    | task      | Task name                                            |
    +-----------+------------------------------------------------------+
    | workspace | Directory of current workspace                       |
    +-----------+------------------------------------------------------+
    | file      | Path to current working file                         |
    +-----------+------------------------------------------------------+

    The above keys default to None so when checking context it can be
    convenient to use attribute access.

    >>> if ctx.project and ctx.task:
    ...     # Do something that depends on a project and task

    '''

    _keys = [
        'platform',
        'user',
        'host',
        'location',
        'mount',
        'project',
        'bin',
        'asset',
        'task',
        'workspace',
        'file',
    ]
    _defaults = {k: None for k in _keys}
    _defaults['user'] = getpass.getuser()
    _defaults['platform'] = PLATFORM
    _defaults['host'] = DEFAULT_HOST

    def __init__(self, **kwargs):
        self.update(**self._defaults)
        self.update(**kwargs)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value

    def copy(self):
        '''Copy this context'''

        return self.__class__(**copy.deepcopy(self))

    def load(self, env=None, **kwargs):
        '''Update ctx with values stored in environment variables. You can
        optionally pass a dictionary to load from. This is different than using
        update because it only updates standard context keys rather than
        updating all keys.
        '''

        env = env or os.environ
        self.update(**kwargs)

        for key in self._keys:
            env_key = ('construct_' + key).upper()
            value = env.get(key, None)
            if value:
                try:
                    self[key] = decode(value)
                except:
                    self[key] = value

    def unload(self):
        '''Restore this Context to defaults'''

        self.clear()
        self.update(**self._defaults)

    def store(self, env=None):
        '''Store this Context in os.environ. You may also pass a dict.'''

        env = env or os.environ
        env.update(self._to_env())

    def _to_env(self):
        '''Serialize ctx to strings storable as environment values.'''

        env = {}
        for key in self._keys:
            env_key = ('construct_' + key).upper()
            value = self.get(key, None)
            if value:
                if isinstance(value, basestring):
                    env[env_key] = value
                else:
                    env[env_key] = encode(value)
        return env
