# -*- coding: utf-8 -*-
from __future__ import absolute_import
import shutil
import sys

from . import data_dir, testAPI
from construct.settings import restore_default_settings
import construct


CUSTOM_USER_PATH = data_dir('.cons')


def setup_module():
    restore_default_settings(CUSTOM_USER_PATH)


def teardown_module():
    shutil.rmtree(str(CUSTOM_USER_PATH))


def test_init():
    '''initialize API'''

    api = testAPI(
        __name__,
        path=[CUSTOM_USER_PATH]
    )
    assert api.settings


def test_uninit():
    '''uninitialize API'''

    api = testAPI(__name__)
    api.uninit()

    assert not api.settings
    assert not api.extensions
