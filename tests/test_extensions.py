# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sys
import os
import shutil

from . import data_dir
from construct.settings import restore_default_settings
from construct.extensions import Extension
import construct

CUSTOM_USER_PATH = data_dir('.cons')


def setup_module():
    restore_default_settings(CUSTOM_USER_PATH)
    construct.API(__name__, path=[CUSTOM_USER_PATH])


def teardown_module():
    shutil.rmtree(CUSTOM_USER_PATH)
    api = construct.API(__name__)
    api.uninit()


class Counter(Extension):

    identifier = 'counter'
    label = 'Counter'
    icon = ''

    def setup(self, api):
        self._count = 0

    def load(self, api):
        api.extend('increment', self.increment)
        api.extend('decrement', self.decrement)
        api.extend('count', self.count)

    def unload(self, api):
        api.unextend('increment')
        api.unextend('decrement')
        api.unextend('count')

    def count(self):
        return self._count

    def increment(self):
        self._count += 1

    def decrement(self):
        self._count -= 1


def test_simple_extension():
    '''Register and use a simple extension'''

    api = construct.API(__name__)
    api.extensions.register(Counter)

    assert hasattr(api, 'increment')
    assert hasattr(api, 'decrement')
    assert hasattr(api, 'count')

    api.increment()
    assert api.count() == 1
    api.decrement()
    assert api.count() == 0

    api.extensions.unregister(Counter)
    assert not hasattr(api, 'increment')
    assert not hasattr(api, 'decrement')
    assert not hasattr(api, 'count')


def test_builtins_loaded():
    '''Ensure all builtin extensions are loaded'''

    import construct.builtins
    api = construct.API(__name__)

    for ext in construct.builtins.extensions:
        assert api.extensions.loaded(ext.identifier)
