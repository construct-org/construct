# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sys
import os
import shutil

from . import data_dir
from construct.settings import restore_default_settings
import construct


CUSTOM_USER_PATH = data_dir('.cons')


def setup_module():
    restore_default_settings(CUSTOM_USER_PATH)


def teardown_module():
    shutil.rmtree(CUSTOM_USER_PATH)


def test_init():
    '''initialize API'''

    api = construct.API(
        __name__,
        path=[CUSTOM_USER_PATH],
        logging=dict(version=1)
    )
    assert api.settings


def test_uninit():
    '''uninitialize API'''

    api = construct.API(__name__)
    api.uninit()

    assert not api.settings
    assert not api.extensions
