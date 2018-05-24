# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from construct.tests import data_path
import construct


def teardown():
    construct.extensions.clear()


def test_discover_single_path():
    '''Discover Extensions on single path'''

    construct.extensions.discover(data_path('extpath1'))
    exts = construct.extensions.collect()
    assert 'ExtensionA' in exts


def test_discover_multiple_paths():
    '''Discover Extensions on multiple paths'''

    construct.extensions.discover(
        data_path('extpath1'),
        data_path('extpath2'),
        data_path('extpath3'),
    )
    exts = construct.extensions.collect()
    assert 'ExtensionA' in exts
    assert 'ExtensionB' in exts
    assert 'ExtensionC' in exts
