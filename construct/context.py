# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import absolute_import
import copy
import getpass
import os
import json

# Third party imports
from past.builtins import basestring

# Local imports
from .constants import DEFAULT_HOST, PLATFORM


__all__ = ['Context']


def encode(obj):
    return json.dumps(obj)


def decode(obj):
    return json.loads(obj)


class Context(dict):
    '''Represents a state used to interact with Construct. The Construct object
    provides both item and attribute access.

    >>> ctx = Context()
    >>> ctx.project = {'name': 'my_project'}
    >>> ctx['project'] == ctx.project

    Context objects can be loaded from and stored in environment variables
    prefixed with **CONSTRUCT_**.

    +----------+------------------------------------------------------+
    |   key    |                     description                      |
    +==========+======================================================+
    | user     | usually the same as the logged in user               |
    +----------+------------------------------------------------------+
    | platform | Current platform [win, linux, mac]                   |
    +----------+------------------------------------------------------+
    | host     | Host application like maya, nuke, standalone, etc... |
    +----------+------------------------------------------------------+
    | project  | Project entity                                       |
    +----------+------------------------------------------------------+
    | folder   | Folder entity                                        |
    +----------+------------------------------------------------------+
    | asset    | Asset entity                                         |
    +----------+------------------------------------------------------+
    | task     | Task entity                                          |
    +----------+------------------------------------------------------+
    | version  | Version entity                                       |
    +----------+------------------------------------------------------+
    | file     | Path to a file                                       |
    +----------+------------------------------------------------------+

    The above keys default to None so when checking context it can be
    convenient to use attribute access.

    >>> if ctx.project and ctx.task:
    ...     # Do something that depends on a project and task

    '''

    _keys = [
        'user',
        'platform',
        'host',
        'platform',
        'project',
        'folder',
        'asset',
        'task',
        'version',
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

    def load(self, env=None):
        '''Update ctx with values stored in environment variables. You can
        optionally pass a dictionary to load from. This is different than using
        update because it only updates standard context keys rather than
        updating all keys.
        '''

        env = env or os.environ
        for key in self._keys:
            value = env.get(('construct_' + key).upper(), None)
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
        env.update(self.to_envvars())

    def to_envvars(self):
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

    def clear_envvars(self):
        '''Clear context stored in environment variables.'''

        for key in self._keys:
            env_key = ('construct_' + key).upper()
            os.environ.pop(env_key, None)

    def copy(self):
        '''Copy this context'''

        return self.__class__(**copy.deepcopy(self))
