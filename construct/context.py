# -*- coding: utf-8 -*-
import copy
import getpass
import os
import sys

from .constants import DEFAULT_HOST, PLATFORM

__all__ = ['Context']


class Context(object):

    def __init__(self):
        self._ctx = {}

    def __str__(self):
        return str(self._ctx)

    def load(self, ctx=None, env=None):
        '''Update ctx with values stored in environment variables.'''

        ctx = ctx or self._ctx
        env = env or os.environ
        ctx['user'] = getpass.getuser()
        ctx['platform'] = PLATFORM
        ctx['host'] = env.get('CONSTRUCT_HOST', DEFAULT_HOST)
        ctx['project'] = env.get('CONSTRUCT_PROJECT', None)
        ctx['folder'] = env.get('CONSTRUCT_FOLDER', None)
        ctx['asset'] = env.get('CONSTRUCT_ASSET', None)
        ctx['task'] = env.get('CONSTRUCT_TASK', None)
        ctx['version'] = env.get('CONSTRUCT_VERSION', None)
        ctx['file'] = env.get('CONSTRUCT_FILE', None)

    def unload(self, ctx=None):
        '''Clear the given context.'''

        ctx = ctx or self._ctx
        ctx.clear()

    def store(self, ctx=None, env=None):
        '''Write ctx values to environment variables'''

        ctx = ctx or self._ctx
        env = env or os.environ
        env.update(self.to_envvars(ctx))

    def update(self, **values):
        self._ctx.update(**values)

    def set(self, ctx):
        self._ctx = ctx

    def to_envvars(self, ctx=None):

        ctx = ctx or self._ctx
        env = {}
        for key in ['host', 'project', 'folder', 'asset', 'task', 'file']:
            env_key = ('construct_' + key).upper()
            value = ctx.get(key, None)
            if value:
                env[env_key] = value
        return env

    def copy(self, ctx=None):
        '''Copy a context or the active context.'''

        ctx = ctx or self._ctx
        return copy.deepcopy(ctx)
