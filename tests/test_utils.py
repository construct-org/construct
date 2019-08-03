# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sys

from construct.compat import Path
from construct.utils import unipath, update_dict


def test_unipath_nonexist():
    '''unipath works with paths that do not exist'''

    path = unipath('~', 'definitely_does_not_exist')
    assert not path.exists()


def test_update_dict():
    '''Test update_dict'''

    software = {
        'label': 'Test Software',
        'icon': 'icons/test.png',
        'host': 'test',
        'cmd': {
            'linux': 'linux_cmd',
            'mac': 'mac_cmd',
            'win': 'win_cmd'
        },
        'extensions': ['.ext']
    }

    update_dict(software, {'cmd': {'linux': 'changed'}, 'extensions': []})

    expected_software = {
        'label': 'Test Software',
        'icon': 'icons/test.png',
        'host': 'test',
        'cmd': {
            'linux': 'changed',
            'mac': 'mac_cmd',
            'win': 'win_cmd'
        },
        'extensions': []
    }
    assert software == expected_software
