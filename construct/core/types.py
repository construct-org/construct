# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from collections import Mapping, deque
from construct.core.util import update_dict


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

    def update(self, other):
        if isinstance(other, Namespace):
            update_dict(self.__dict__, other.__dict__)
        elif isinstance(other, Mapping):
            update_dict(self.__dict__, other)
        else:
            raise TypeError('Argument must be a Namespace or Mapping instance')


class Stack(deque):

    def push(self, item):
        self.append(item)

    def size(self):
        return len(self)

    def empty(self):
        return not self

    def top(self):
        return self[-1]
