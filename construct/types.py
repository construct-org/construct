# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

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
    'INTEGRATE'
]

import abc
from collections import Mapping, deque
from construct.util import update_dict


ABC = abc.ABCMeta('ABC', (object,), {})


class Namespace(object):

    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join(['='.join([k, v]) for k, v in self.__dict__.items()])
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

STAGE = Priority(0, 'Stage', 'Stage data')
VALIDATE = Priority(1, 'Validate', 'Validate data')
REPAIR = Priority(2, 'Repair', 'Repair data')
COMMIT = Priority(3, 'Commit', 'Commit new artifacts')
INTEGRATE = Priority(4, 'Integrate', 'Integrate artifacts')

DEFAULTS = {
    (0, None, None): STAGE0,
    (1, None, None): STAGE1,
    (2, None, None): STAGE2,
    (3, None, None): STAGE3,
    (4, None, None): STAGE4,
}
Priority._instances.update(DEFAULTS)
