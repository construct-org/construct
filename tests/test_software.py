# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sys
import os
import shutil

from . import data_dir, setup_api, teardown_api
import construct
from construct.errors import InvalidSettings


SOFTWARE_NAME = 'testsoftware'
SOFTWARE_SETTINGS = dict(
    label='Test Software',
    icon='icons/test_software.png',
    host='TestSoftware',
    cmd=dict(
        linux='/usr/bin/testsoftware',
        mac='/Applications/testsoftware.app/bin/testsoftware',
        win='C:/Program Files/testsoftware/bin/testsoftware.exe'
    ),
    extensions=['.tsb']
)
SOFTWARE_FILE = data_dir(
    __name__,
    'settings',
    'software',
    SOFTWARE_NAME + '.yaml'
)


def setup_module():
    setup_api(__name__)


def teardown_module():
    teardown_api(__name__)


def test_save_software():
    '''Save software to settings'''

    api = construct.API(__name__)
    api.save_software(
        SOFTWARE_NAME,
        SOFTWARE_SETTINGS
    )
    assert SOFTWARE_NAME in api.get_software()
    assert SOFTWARE_FILE.is_file()


def test_project_software():
    '''Add and update project software.'''

    api = construct.API(__name__)
    project = api.io.new_project(
        'test',
        location='local',
        mount='projects'
    )
    api.save_software(
        'app',
        {
            'label': 'App',
            'host': 'app',
            'cmd': {},
            'icon': 'icons/app.png'
        },
        project=project
    )
    project_software = api.get_software(project=project)
    assert 'app' in project_software

    project_software = api.update_software(
        'app',
        {'extensions': ['.ext'], 'cmd': {'win': 'changed'}},
        project=project
    )
    assert project_software['extensions'] == ['.ext']
    assert project_software['cmd']['win'] == 'changed'


def test_delete_software():
    '''Delete software from settings'''

    api = construct.API(__name__)
    assert SOFTWARE_NAME in api.settings['software']
    assert SOFTWARE_FILE.is_file()

    api.delete_software(SOFTWARE_NAME)
    assert SOFTWARE_NAME not in api.settings['software']
    assert not SOFTWARE_FILE.is_file()
