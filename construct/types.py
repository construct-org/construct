# -*- coding: utf-8 -*-
from __future__ import absolute_import

# Standard library imports
import weakref


class WeakRef(weakref.ref):
    '''Same as weakref.ref but supports attribute assignment.'''


class WeakMeth(object):
    '''weakref.ref for methods.'''

    def __init__(self, obj, callback=None):
        self.name = obj.__name__
        self.ref = WeakRef(obj.__self__, callback)

    def __call__(self):
        inst = self.ref()
        if inst is None:
            return
        return getattr(inst, self.name)


class StrongRef(object):
    '''Hold a reference to an object.'''

    def __init__(self, obj, callback=None):
        self.name = obj.__name__
        self.obj = obj

    def __call__(self):
        return self.obj


class WeakSet(object):
    '''A weakset implementation that supports methods. The underlying
    data is stored as list so it will remain ordered unlike a true set.
    '''

    def __init__(self, iterator=None):
        self._refs = []
        self._ids = []

        if iterator is not None:
            for item in iterator:
                self.add(item)

    def __len__(self):
        return len(self._ids)

    def __contains__(self, obj):
        return (
            obj in self._ids or
            obj in self._refs or
            self._ref_id(obj) in self._ids
        )

    def __iter__(self):
        for ref in self._refs:
            obj = ref()
            if obj is None:
                continue
            yield obj

    def _ref_id(self, obj):
        if is_method(obj):
            if hasattr(obj, '__func__'):
                return id(obj.__self__), id(obj.__func__)
            return id(obj.__self__), id(obj.__name__)
        else:
            return id(obj)

    def _remove_ref(self, ref):
        ref_id = ref.ref_id
        if ref_id not in self._ids:
            return

        index = self._ids.index(ref_id)
        self._ids.pop(index)
        self._refs.pop(index)

    def add(self, obj, strong=False):
        ref_id = self._ref_id(obj)
        if ref_id in self._ids:
            return

        self._ids.append(ref_id)
        if strong:
            ref = StrongRef(obj)
            ref.ref_id = ref_id
        elif is_method(obj):
            ref = WeakMeth(obj, self._remove_ref)
            ref.ref.ref_id = ref_id
        else:
            ref = WeakRef(obj, self._remove_ref)
            ref.ref_id = ref_id

        self._refs.append(ref)

    def discard(self, obj):
        ref_id = self._ref_id(obj)
        if ref_id not in self._ids:
            return

        index = self._ids.index(ref_id)
        self._ids.pop(index)
        self._refs.pop(index)


def is_method(obj):
    return hasattr(obj, '__call__') and hasattr(obj, '__self__')
