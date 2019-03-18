# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
from construct.utils import unipath

this_dir = os.path.abspath(os.path.dirname(__file__))


def test_dir(*paths):
    return unipath(this_dir, *paths)


def data_dir(*paths):
    return test_dir('data', *paths)
