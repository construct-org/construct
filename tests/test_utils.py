# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function

# Standard library imports
import os

# Local imports
from construct.constants import PLATFORM
from construct.utils import unipath, update_dict, update_env


def test_unipath_nonexist():
    '''unipath works with paths that do not exist'''

    path = unipath('~', 'definitely_does_not_exist')
    assert not path.exists()


def test_update_dict():
    '''Update dict'''

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


def test_update_env():
    '''Update environment dict'''

    env = {
        'insert_list': 'E',
        'update_string': 'E',
        'plat_list': 'E',
    }
    upd = {
        'plat_list': {
            'win': ['W0', 'W1'],
            'linux': ['L0'],
            'mac': ['M0', 'M1'],
        },
        'insert_list': ['U0', 'U1'],
        'update_string': 'U',
        'new_list': ['U0', 'U1'],
        'new_string': 'U',
        'plat_string': {'win': 'W', 'linux': 'L', 'mac': 'M'},
    }
    expected = {
        'plat_list': os.pathsep.join(upd['plat_list'][PLATFORM] + ['E']),
        'insert_list': os.pathsep.join(['U0', 'U1', 'E']),
        'update_string': 'U',
        'new_list': os.pathsep.join(['U0', 'U1']),
        'new_string': 'U',
        'plat_string': upd['plat_string'][PLATFORM],
    }

    result = env.copy()
    update_env(result, **upd)
    assert result == expected
