# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
import os
from types import ModuleType
from nose.tools import raises
from construct import Construct, RegistrationError
from construct.plugins import discover
from construct.tests import data_path


def test_discover_single_path():
    '''Discover plugins on single path'''

    plugins = discover(data_path('plugin_path1'))
    assert 'plugin1' in plugins
    assert 'plugin2' in plugins
    assert isinstance(plugins['plugin1'], ModuleType)
    assert isinstance(plugins['plugin2'], ModuleType)


def test_discover_multiple_paths():
    '''Discover plugins on multiple paths'''

    plugins = discover(
        data_path('plugin_path1'),
        data_path('plugin_path2'),
        data_path('plugin_path3'),
    )
    assert 'plugin1' in plugins
    assert (
        os.path.normpath(plugins['plugin1'].__file__)
        ==
        os.path.normpath(data_path('plugin_path1', 'plugin1', '__init__.pyc'))
    )
    assert 'plugin2' in plugins
    assert (
        os.path.normpath(plugins['plugin2'].__file__)
        ==
        os.path.normpath(data_path('plugin_path1', 'plugin2.py'))
    )
    assert 'plugin3' in plugins
    assert 'plugin4' in plugins
    assert 'notplugin5' not in plugins


def test_construct_discover_paths():
    '''Discover plugins in Construct.__init__'''

    cons = Construct(plugin_paths=[
        data_path('plugin_path1'),
        data_path('plugin_path2'),
        data_path('plugin_path3'),
    ])
    plugins = cons.get_plugins()
    assert 'plugin1' in plugins
    assert (
        os.path.normpath(plugins['plugin1'].__file__)
     == os.path.normpath(data_path('plugin_path1', 'plugin1', '__init__.pyc'))
    )
    assert 'plugin2' in plugins
    assert (
        os.path.normpath(plugins['plugin2'].__file__)
     == os.path.normpath(data_path('plugin_path1', 'plugin2.py'))
    )
    assert 'plugin3' in plugins
    assert 'plugin4' in plugins
    assert 'notplugin5' not in plugins


@raises(RegistrationError)
def test_construct_discover_exc():
    '''Discover plugins in Construct.__init__ that raise exceptions'''

    Construct(plugin_paths=[data_path('plugin_path_exc')])
