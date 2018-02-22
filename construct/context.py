# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

__all__ = [
    'Context',
    'from_env',
    'from_path',
    'current_cons',
    'context',
    'request',
    'to_env',
    'to_env_dict',
]

import os
import sys
import fsfs
from fstrings import f
from collections import Mapping
from werkzeug.local import LocalStack, LocalProxy


_cons_stack = LocalStack()
current_cons = LocalProxy(_cons_stack, 'top')

_ctx_stack = LocalStack()
context = LocalProxy(_ctx_stack, 'top')

_req_stack = LocalStack()
request = LocalProxy(_req_stack, 'top')

_action_stack = LocalStack()
action = LocalProxy(_action_stack, 'top')


class Context(object):

    _keys = [
        'host',
        'root',
        'project',
        'sequence',
        'shot',
        'asset',
        'task',
        'workspace',
        'platform'
    ]
    _entry_order = [
        'project',
        'sequence',
        'shot',
        'asset',
        'task',
        'workspace'
    ]
    _defaults = {k: None for k in _keys}
    _defaults['platform'] = sys.platform.rstrip('0123456789').lower()

    def __init__(self, **kwargs):
        kwargs = dict(self._defaults, **kwargs)
        self.__dict__.update(kwargs)

    def __repr__(self):
        kwargs = ', '.join([f('{k}={v}') for k, v in self.__dict__.items()])
        return f('{self.__class__.__name__}({kwargs})')

    def __enter__(self):
        self.push()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.pop()
        raise exc_type, exc_value, tb

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
        for key in reversed(self._entry_order):
            entry = self.__dict__.get(key, None)
            if entry:
                return entry

    def update(self, other, exclude=['host']):
        if isinstance(other, Context):
            other = other.__dict__

        if isinstance(other, Mapping):
            if exclude:
                other = {k:v for k, v in other.items() if k not in exclude}
            self.__dict__.update(other)
        else:
            raise TypeError('Not a Mapping or Context: ', other)


def to_env_dict(context, exclude=['host']):
    '''Push context to environment variables...'''

    d = {}
    for key in context._keys:

        if key in exclude:
            continue

        value = getattr(context, key)
        if value is not None:
            d['CONSTRUCT_' + key.upper()] = str(value)
    return d


def to_env(context, exclude=['host']):
    '''Push context to environment variables...'''

    for key in context._keys:

        if key in exclude:
            continue

        value = getattr(context, key)
        if value is not None:
            os.environ['CONSTRUCT_' + key.upper()] = str(value)


def from_env():
    '''Create new context from environment variables'''


    ctx = dict(
        root=os.environ.get('CONSTRUCT_ROOT', os.getcwd()),
        host=os.environ.get('CONSTRUCT_HOST', None),
    )
    entries = ['project', 'asset', 'sequence', 'shot', 'task', 'workspace']
    for entry in entries:
        env_var = 'CONSTRUCT_' + entry.upper()
        value = os.environ.get(env_var, None)
        if value:
            value = fsfs.get_entry(value)
        ctx[entry] = value

    return Context(**ctx)


def from_path(path):
    '''Extract context from file path.'''

    ctx = from_env()

    if os.path.isfile(path):
        path = os.path.dirname(path)

    for entry in fsfs.search(path, direction=fsfs.UP):
        tags = entry.tags
        for key in Context._keys:
            if key in tags:
                setattr(ctx, key, entry)

    return ctx
