# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from nose.tools import raises, assert_raises
from construct.tests import data_path
import construct


def teardown():
    construct.extensions.clear()


def test_discover_single_path():
    '''Discover plugins on single path'''

    construct.extensions.discover(data_path('extpath1'))
    exts = construct.extensions.collect()
    assert 'ExtensionA' in exts
    assert len(exts) == 1


def test_discover_multiple_paths():
    '''Discover plugins on multiple paths'''

    construct.extensions.discover(
        data_path('extpath1'),
        data_path('extpath2'),
        data_path('extpath3'),
    )
    exts = construct.extensions.collect()
    assert 'ExtensionA' in exts
    assert 'ExtensionB' in exts
    assert 'ExtensionC' in exts
    assert len(exts) == 3


@raises(RuntimeError)
def test_construct_discover_exc():
    '''Discover plugins in Construct.__init__ that raise exceptions'''

    construct.extensions.discover(
        data_path('extpath4_wexc')
    )
