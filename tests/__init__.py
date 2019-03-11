# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os


this_dir = os.path.abspath(os.path.dirname(__file__))


def test_dir(*paths):
    return os.path.join(this_dir, *paths).replace('\\', '/')


def data_dir(*paths):
    return test_dir('data', *paths)
