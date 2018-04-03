# -*- coding: utf-8 -*-
from __future__ import absolute_import
from construct import types


def test_weakset_bound_methods():
    '''Weakset with bound methods'''


    class Object(object):

        def method_a(self):
            pass

        def method_b(self):
            pass

    weakset = types.weakset()

    a = Object()
    b = Object()

    weakset.add(a.method_a)
    weakset.add(a.method_b)
    weakset.add(b.method_a)
    weakset.add(b.method_b)
    assert len(weakset) == 4

    del(b)
    assert len(weakset) == 2

    weakset.add(a.method_a)
    weakset.add(a.method_b)
    assert len(weakset) == 2

    del(a)
    assert len(weakset) == 0


def test_weakset_functions():
    '''Weakset with functions'''

    weakset = types.weakset()

    def func():
        pass

    weakset.add(func)
    assert len(weakset) == 1

    weakset.add(func)
    assert len(weakset) == 1

    del(func)
    assert len(weakset) == 0
