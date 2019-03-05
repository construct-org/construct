# -*- coding: utf-8 -*-
from __future__ import absolute_import
import copy
import os
import shutil
import sys
import logging

from builtins import open
import yaml

from . import schemas
from .constants import (
    SETTINGS_FILE,
    USER_SETTINGS_FILE,
    DEFAULT_SETTINGS,
    USER_PATH
)
from .utils import unipath, ensure_exists
from .errors import InvalidSettings


_log = logging.getLogger(__name__)


class Settings(dict):
    '''Provides dict access to the settings file.'''

    structure = [
        'software',
        'extensions',
        'icons',
        'templates'
    ]

    def __init__(self, path):
        self.path = path
        self.file = None
        self.folder = None
        self.is_loaded = False

    def get_software(self):
        v = schemas.get_validator('software')

        software = {}
        software_folder = unipath(self.folder, 'software')
        if not os.path.isdir(software_folder):
            return software

        for f in os.listdir(software_folder):

            if not f.endswith('.yml') and not f.endswith('.yaml'):
                continue

            software_name = os.path.splitext(f)[0]
            software_file = unipath(software_folder, f)
            with open(software_file, 'r') as sf:
                software_data = yaml.load(sf.read())
            software_data = v.validated(software_data)
            if not software_data:
                raise InvalidSettings(
                    software_file + ' contains the following errors:\n' +
                    v.errors_yaml
                )
            software_data['file'] = software_file
            software_data['name'] = software_name
            software[software_name] = software_data

        return software

    def save_software(self, name, **data):

        v = schemas.get_validator('software')
        software = v.validated(data)
        if not software:
            raise InvalidSettings(
                'Can not add software got the following errors:\n' +
                v.errors_yaml
            )

        self['software'][name] = software

        software_file = unipath(self.folder, 'software', name + '.yaml')
        with open(software_file, 'w') as f:
            f.write(yaml.dump(software, default_flow_style=False))

    def delete_software(self, name):

        self['software'].pop(name, None)
        software_file = unipath(self.folder, 'software', name + '.yaml')
        if os.path.isfile(software_file):
            os.remove(software_file)

    def load(self):
        v = schemas.get_validator('settings')
        if not v.validate(DEFAULT_SETTINGS):
            raise InvalidSettings(
                'DEFAULT_SETTINGS have the following errors:\n' +
                v.errors_yaml
            )

        self.update(**DEFAULT_SETTINGS)
        self.file = USER_SETTINGS_FILE
        potential_settings_file = find_in_paths(self.path, SETTINGS_FILE)

        if potential_settings_file:
            self.file = potential_settings_file
            _log.debug('Loading settings from %s' % self.file)

            with open(self.file, 'rb') as f:
                file_data = yaml.load(f.read())

            if not v.validate(file_data):
                raise InvalidSettings(
                    self.file + ' contains the following errors:\n' +
                    v.errors_yaml
                )

            self.update(**file_data)
        else:
            _log.debug(
                'Settings file not found.'
                ' Writing default settings to ' + self.file
            )
            restore_default_settings(USER_PATH)

        self.folder = os.path.dirname(self.file)

        # Make sure our settings folders exist
        ensure_exists(*[unipath(self.folder, f) for f in self.structure])

        self.update(software=self.get_software())
        self.is_loaded = True

    def unload(self):
        self.clear()
        self.file = None
        self.folder = None
        self.is_loaded = False

    def save(self):
        if self.is_loaded:
            with open(self.file, 'wb') as f:
                f.write(self.yaml(exclude=['software']))

    def yaml(self, exclude=None):
        settings_to_encode = copy.deepcopy(dict(self))
        exclude = (exclude or [])
        for key in exclude:
            settings_to_encode.pop(key, None)
        return yaml.safe_dump(settings_to_encode, default_flow_style=False)


def restore_default_settings(where):
    '''Create a default configuration in the provided folder.'''

    if os.path.isdir(where):
        shutil.rmtree(where)

    ensure_exists(where)
    ensure_exists(*[unipath(where, f) for f in Settings.structure])

    settings_file = unipath(where, SETTINGS_FILE)
    encoded = yaml.safe_dump(DEFAULT_SETTINGS, default_flow_style=False)
    with open(settings_file, 'wb') as f:
        f.write(encoded)


def find_in_paths(paths, resource):
    '''Find a resource in a list of paths'''

    for path in paths:
        potential_path = unipath(path, resource)
        if os.path.exists(potential_path):
            return potential_path
