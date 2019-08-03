# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sys

from construct.compat import Path
from construct.utils import unipath, update_dict


def test_unipath_nonexist():
    '''unipath works with paths that do not exist'''

    path = unipath('~', 'definitely_does_not_exist')
    assert not path.exists()



def test_unipath_nonexist():
    '''unipath works with paths that do not exist'''

    path = unipath('~', 'definitely_does_not_exist')
    assert not path.exists()
