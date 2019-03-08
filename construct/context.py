# -*- coding: utf-8 -*-
from __future__ import absolute_import
import copy
import getpass
import os
import sys
import json

from past.builtins import basestring
from .constants import DEFAULT_HOST, PLATFORM

__all__ = ['Context']


def encode(obj):
    return json.dumps(obj)


def decode(obj):
    return json.loads(obj)


class Context(dict):

    _keys = [
        'user',
        'platform',
        'host',
        'user',
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

    def copy(self):
        '''Copy this context'''

        return self.__class__(**copy.deepcopy(self))
