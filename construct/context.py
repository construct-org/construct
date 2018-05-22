# -*- coding: utf-8 -*-
from __future__ import absolute_import

__all__ = [
    'Context',
    '_ctx_stack',
    '_req_stack',
]

import os
import fsfs
from getpass import getuser
from collections import Mapping
from werkzeug.local import LocalStack
from construct.constants import DEFAULT_ROOT, DEFAULT_HOST
from construct.utils import platform, unipath
from construct.models import is_entry


_ctx_stack = LocalStack()
_req_stack = LocalStack()


class Context(object):

    keys = [
        'host',
        'root',
        'user',
        'project',
        'collection',
        'sequence',
        'shot',
        'asset_type',
        'asset',
        'task',
        'workspace',
        'platform',
        'file'
    ]
    entry_keys = [
        'project',
        'collection',
        'sequence',
        'shot',
        'asset_type',
        'asset',
        'task',
        'workspace',
        'file'
    ]
    defaults = {k: None for k in keys}
    defaults['platform'] = platform
    defaults['user'] = getuser()

    def __init__(self, **kwargs):
        kwargs = dict(self.defaults, **kwargs)
        self.__dict__.update(kwargs)

    def __repr__(self):
        kwargs = ', '.join(
            [('{}={}').format(k, v) for k, v in self.__dict__.items()]
        )
        return '{}({})'.format(self.__class__.__name__, kwargs)

    def __enter__(self):
        self.push()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.pop()

    def __getitem__(self, key):
        return self.__dict__.__getitem__(key)

    def __setitem__(self, key, value):
        self.__dict__.__setitem__(key, value)

    def __contains__(self, key):
        return self.__dict__.__contains__(key)

    def push(self):
        _ctx_stack.push(self)

    def pop(self):
        if _ctx_stack.top is self:
            _ctx_stack.pop()

    def get_deepest_entry(self):
        for key in reversed(self.entry_keys):
            entry = self.__dict__.get(key, None)
            if entry and is_entry(entry):
                return entry

    def update(self, other, exclude=['host']):
        if isinstance(other, Context):
            other = other.__dict__

        if isinstance(other, Mapping):
            if exclude:
                other = {k: v for k, v in other.items() if k not in exclude}
            self.__dict__.update(other)
        else:
            raise TypeError('Not a Mapping or Context: ', other)

    def to_env_dict(self, exclude=None):
        '''Push context to environment variables...'''

        exclude = exclude or ['host']
        data = {}
        for key in self.keys:

            if key in exclude:
                continue

            value = getattr(self, key)
            if value is not None:
                data['CONSTRUCT_' + key.upper()] = str(value)
        return data

    def to_env(self, exclude=None):
        '''Push context to environment variables...'''

        exclude = exclude or ['host']

        for key in self.keys:

            if key in exclude:
                continue

            value = getattr(self, key)
            if value is not None:
                os.environ['CONSTRUCT_' + key.upper()] = str(value)

    @classmethod
    def from_env(cls, exclude=None):
        '''Create new context from environment variables'''

        data = dict(
            root=os.environ.get('CONSTRUCT_ROOT', DEFAULT_ROOT),
            host=os.environ.get('CONSTRUCT_HOST', DEFAULT_HOST),
        )
        for entry in cls.entry_keys:
            env_var = 'CONSTRUCT_' + entry.upper()
            value = os.environ.get(env_var, None)
            if value:
                value = fsfs.get_entry(value)
            data[entry] = value

        return cls(**data)

    @classmethod
    def from_path(cls, path):
        '''Extract context from file path'''

        ctx = Context.from_env()

        if os.path.isfile(path):
            ctx.file = unipath(path)
            path = os.path.dirname(path)

        for entry in fsfs.search(path, direction=fsfs.UP):
            tags = entry.tags
            for key in Context.entry_keys:
                if key in tags:
                    setattr(ctx, key, entry)

        return ctx
