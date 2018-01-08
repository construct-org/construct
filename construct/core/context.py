'''
context class
=============
'''
import os
import fsfs
from fstrings import f
from construct.core.util import update_dict
from collections import Mapping

__all__ = ['Context', 'from_env', 'from_path']


class Namespace(object):

    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)

    def __repr__(self):
        kwargs = [f('{k}={v}') for k, v in self.__dict__.items()]
        kwargs = ', '.join(kwargs)
        return f('{self.__class__.__name__}({kwargs})')

    def __contains__(self, key):
        return key in self.__dict__

    def __getitem__(self, key):
        return self.__dict__.__getitem__(key)

    def __setitem__(self, key, value):
        return self.__dict__.__setitem__(key, value)

    def update(self, other):
        if isinstance(other, Namespace):
            update_dict(self.__dict__, other.__dict__)
        elif isinstance(other, Mapping):
            update_dict(self.__dict__, other)
        else:
            raise TypeError('Argument must be a Namespace or Mapping instance')


class Context(Namespace):

    _keys = [
        'host',
        'root',
        'project',
        'sequence',
        'shot',
        'asset',
        'workspace',
        'selection',
    ]
    _defaults = {k: None for k in _keys}

    def __init__(self, **kwargs):
        kwargs = dict(self._defaults, **kwargs)
        super(Context, self).__init__(**kwargs)


def to_env(context):
    '''Push context to environment variables...'''

    for key in context._keys:
        value = getattr(context, key)
        if value is not None:
            os.environ['CONSTRUCT_' + key.upper()] = value


def merge(a, b, exclude=['root', 'host']):
    '''Join two contexts'''

    context = Context(**a.__dict__)
    for k, v in b.__dict__.items():
        if k not in exclude:
            context.__dict__[k] = v
    return context


def from_env():
    '''Create new context from environment variables'''

    ctx = dict(
        root=os.environ.get('CONSTRUCT_ROOT', os.getcwd()),
        host=os.environ.get('CONSTRUCT_HOST', None),
        project=os.environ.get('CONSTRUCT_PROJECT', None),
        asset=os.environ.get('CONSTRUCT_ASSET', None),
        sequence=os.environ.get('CONSTRUCT_SEQUENCE', None),
        shot=os.environ.get('CONSTRUCT_SHOT', None),
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
