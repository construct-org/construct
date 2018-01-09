'''
context class
=============
'''
import os
import fsfs
from fstrings import f
from construct.core.globals import _ctx_stack
from collections import Mapping

__all__ = ['Context', 'from_env', 'from_path']


class Context(object):

    _keys = [
        'host',
        'root',
        'project',
        'sequence',
        'shot',
        'asset',
        'workspace',
    ]
    _defaults = {k: None for k in _keys}

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
        if _ctx_stack.top() is self:
            _ctx_stack.pop()

    def update(self, other):
        if isinstance(other, Mapping):
            self.__dict__.update(other)
        elif isinstance(other, Context):
            self.__dict__.update(other.__dict__)
        raise TypeError('Not a Mapping or Context: ', other)


def to_env(context):
    '''Push context to environment variables...'''

    for key in context._keys:
        value = getattr(context, key)
        if value is not None:
            os.environ['CONSTRUCT_' + key.upper()] = value


def from_env():
    '''Create new context from environment variables'''

    ctx = dict(
        root=os.environ.get('CONSTRUCT_ROOT', os.getcwd()),
        host=os.environ.get('CONSTRUCT_HOST', None),
        project=os.environ.get('CONSTRUCT_PROJECT', None),
        asset=os.environ.get('CONSTRUCT_ASSET', None),
        sequence=os.environ.get('CONSTRUCT_SEQUENCE', None),
        shot=os.environ.get('CONSTRUCT_SHOT', None),
        workspace=os.environ.get('CONSTRUCT_WORKSPACE', None)
    )
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
                setattr(ctx, key, entry.name)

    return ctx
