# -*- coding: utf-8 -*-
from __future__ import absolute_import

__all__ = [
    'ABC',
    'Namespace',
    'Stack',
    'Priority',
    'STAGE0',
    'STAGE1',
    'STAGE2',
    'STAGE3',
    'STAGE4',
    'STAGE',
    'VALIDATE',
    'REPAIR',
    'COMMIT',
    'INTEGRATE',
    'weakset',
    'weakmeth',
]

import abc
import inspect
import weakref
from collections import Mapping, deque
from construct.utils import update_dict

# Use for type checking with isinstance
from construct.models import Entry  # Bring this in for api convenience
Number = (int, float)

# Alias some six types
import six
Binary = six.binary_type
Integer = six.integer_types
Object = six.class_types
Text = six.text_type
if six.PY2:
    String = (str, unicode)
else:
    String = str

# py2-3 compatible ABCMeta
ABC = abc.ABCMeta('ABC', (object,), {})


class Namespace(object):

    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join(
                [('{}={}').format(k, v) for k, v in self.__dict__.items()]
            )
        )

    def __contains__(self, key):
        return key in self.__dict__

    def __getitem__(self, key):
        return self.__dict__.__getitem__(key)

    def __setitem__(self, key, value):
        return self.__dict__.__setitem__(key, value)

    def items(self):
        return self.__dict__.items()

    def values(self):
        return self.__dict__.values()

    def keys(self):
        return self.__dict__.keys()

    def update(self, other):
        if isinstance(other, Namespace):
            update_dict(self.__dict__, other.__dict__)
        elif isinstance(other, Mapping):
            update_dict(self.__dict__, other)
        else:
            raise TypeError('Argument must be a Namespace or Mapping instance')


class Stack(deque):

    def push(self, item):
        self.appendleft(item)

    def size(self):
        return len(self)

    def empty(self):
        return not self

    def top(self):
        return self[-1]


# Priority Type and Defaults


class Priority(int):

    _instances = {}

    def __new__(cls, value, label=None, description=None):

        key = (value, label, description)
        if key in cls._instances:
            return cls._instances[key]

        if label is None:
            label = 'Priority-' + str(value)

        if description is None:
            description = 'Priority ' + str(value)

        key = (value, label, description)
        if key in cls._instances:
            return cls._instances[key]

        obj = super(Priority, cls).__new__(cls, value)
        obj.label = label
        obj.description = description

        return cls._instances.setdefault(key, obj)


STAGE0 = Priority(0, 'Stage-0', 'First stage')
STAGE1 = Priority(1, 'Stage-1', 'Second stage')
STAGE2 = Priority(2, 'Stage-2', 'Third stage')
STAGE3 = Priority(3, 'Stage-3', 'Fourth stage')
STAGE4 = Priority(4, 'Stage-4', 'Fifth stage')

STAGE = Priority(0, 'Stage', 'Stage')
VALIDATE = Priority(1, 'Validate', 'Validate')
REPAIR = Priority(2, 'Repair', 'Repair')
COMMIT = Priority(3, 'Commit', 'Commit')
INTEGRATE = Priority(4, 'Integrate', 'Integrate artifacts')

DEFAULTS = {
    (0, None, None): STAGE0,
    (1, None, None): STAGE1,
    (2, None, None): STAGE2,
    (3, None, None): STAGE3,
    (4, None, None): STAGE4,
}
Priority._instances.update(DEFAULTS)


class weakset(object):
    '''Like WeakSet but works with bound methods'''

    def __init__(self):
        self._ids = []
        self._refs = []

    def __repr__(self):
        return (
            '<{}>(_ids={}, _refs={})'
        ).format(
            self.__class__.__name__,
            self._ids,
            self._refs
        )

    def __len__(self):
        return len(self._refs)

    def __iter__(self):
        for i in range(len(self._refs)):
            id_ = self._ids.pop(0)
            ref = self._refs.pop(0)
            obj = ref()
            if obj is not None:
                yield obj
                self._refs.append(ref)
                self._ids.append(id_)

    def discard(self, obj):
        if obj not in self._refs:
            return

        index = self._refs.index(obj)
        self._ids.pop(index)
        self._refs.pop(index)

    def add(self, obj):
        id_ = weak_id(obj)

        if id_ in self._ids:
            return

        self._ids.append(id_)

        if inspect.ismethod(obj):
            self._refs.append(weakmeth(obj, self.discard))
        else:
            self._refs.append(weakref.ref(obj, self.discard))


def weak_id(obj):
    '''Returns a unique and constant id for an object including bound meths.'''

    if inspect.ismethod(obj):
        return id(obj.__self__) + id(obj.__func__)
    else:
        return id(obj)


class weakmeth(object):
    '''Like weakref but for bound methods'''

    def __init__(self, meth, callback=None):
        self.name = meth.__name__
        self.ref = weakref.ref(meth.__self__, lambda _: callback(self))

    def __call__(self):
        obj = self.ref()
        if obj is None:
            return
        return getattr(obj, self.name, None)
