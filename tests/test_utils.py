# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sys

from construct.compat import Path
from construct.utils import unipath


def test_path_resolve_bug():
    '''pathlib2 resolve bug exists'''

    try:
        Path('~/definitely_does_not_exist').resolve()
    except WindowsError:
        assert True

    if sys.version_info[0] < 3:
        assert False, 'Remove the Path.resolve patch...'


def test_unipath_nonexist():
    '''unipath works with paths that do not exist'''

    path = unipath('~', 'definitely_does_not_exist')
    assert not path.exists()
