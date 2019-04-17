# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sys
import os
import shutil

from . import data_dir
from construct.settings import Settings, restore_default_settings
from construct.constants import DEFAULT_SETTINGS


SETTINGS_FOLDER = data_dir('.cons')
SETTINGS_FOLDERS = [data_dir('.cons', f) for f in Settings.structure]
SETTINGS_FILE = data_dir('.cons', 'construct.yaml')
CONSTRUCT_PATH = [SETTINGS_FOLDER]
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
SOFTWARE_FILE = data_dir('.cons', 'software', SOFTWARE_NAME + '.yaml')
NEW_LOCATIONS = dict(
    local=dict(
        projects='~/projects',
        lib='~/lib'
    ),
    remote=dict(
        projects='//remote/projects',
        lib='//remote/lib',
    )
)


def teardown_module():
    shutil.rmtree(str(SETTINGS_FOLDER))


def test_create_default_settings():
    '''Create default settings'''

    restore_default_settings(SETTINGS_FOLDER)
    assert SETTINGS_FOLDER.is_dir()
    assert SETTINGS_FILE.is_file()
    assert all([f.is_dir() for f in SETTINGS_FOLDERS])

    settings = Settings(CONSTRUCT_PATH)
    settings.load()
    assert settings.file == SETTINGS_FILE
    assert settings.folder == SETTINGS_FOLDER


def test_save_settings():
    '''Save modified settings'''

    settings = Settings(CONSTRUCT_PATH)
    settings.load()
    settings['locations'] = NEW_LOCATIONS
    settings.save()

    settings = Settings(CONSTRUCT_PATH)
    settings.load()
    assert settings['locations'] == NEW_LOCATIONS


def test_restore_default_settings():
    '''Restore default settings'''

    restore_default_settings(SETTINGS_FOLDER)
    settings = Settings(CONSTRUCT_PATH)
    settings.load()
    for k, v in DEFAULT_SETTINGS.items():
        assert settings[k] == v


def test_save_software():
    '''Save software to settings'''

    settings = Settings(CONSTRUCT_PATH)
    settings.load()
    settings.save_software(
        SOFTWARE_NAME,
        **SOFTWARE_SETTINGS
    )
    assert SOFTWARE_NAME in settings['software']
    assert SOFTWARE_FILE.is_file()


def test_delete_software():
    '''Delete software from settings'''

    settings = Settings(CONSTRUCT_PATH)
    settings.load()
    assert SOFTWARE_NAME in settings['software']
    assert SOFTWARE_FILE.is_file()

    settings.delete_software(SOFTWARE_NAME)
    assert SOFTWARE_NAME not in settings['software']
    assert not SOFTWARE_FILE.is_file()
