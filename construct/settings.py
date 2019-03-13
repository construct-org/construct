# -*- coding: utf-8 -*-
from __future__ import absolute_import
import copy
import os
import shutil
import sys
import logging

from builtins import open, bytes
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
    '''Provides dict access to your settings file.

    Attributes:
        path: :class:`construct.path.Path` used to locate settings
        file: Path to construct.yaml file
        folder: Path containing construct.yaml file
    '''

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

            with open(software_file, 'rb') as sf:
                data = sf.read().decode('utf-8')
                software_data = yaml.load(data)

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
        '''Save a new software configuration.

        Arguments:
            name (str): The name of the software like "maya2019"
            **data: Software settings must match the settings.yaml schema
        '''

        v = schemas.get_validator('software')
        software = v.validated(data)
        if not software:
            raise InvalidSettings(
                'Can not add software got the following errors:\n' +
                v.errors_yaml
            )

        self['software'][name] = software

        software_file = unipath(self.folder, 'software', name + '.yaml')
        data = yaml.dump(software, default_flow_style=False)
        with open(software_file, 'wb') as f:
            f.write(bytes(data, 'utf-8'))

    def delete_software(self, name):
        '''Delete a software configuration

        Arguments:
            name (str): The name of the software like "maya2019"
        '''

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
        self.file = unipath(self.path[-1], SETTINGS_FILE)
        potential_settings_file = find_in_paths(self.path, SETTINGS_FILE)

        if potential_settings_file:
            self.file = potential_settings_file
            _log.debug('Loading settings from %s' % self.file)

            with open(self.file, 'rb') as f:
                data = f.read().decode('utf-8')
                if data:
                    file_data = yaml.load(data)
                else:
                    file_data = {}

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
            restore_default_settings(self.path[-1])

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
        '''Save these settings.'''

        if self.is_loaded:
            data = bytes(self.yaml(exclude=['software']), 'utf-8')
            with open(self.file, 'wb') as f:
                f.write(data)

    def yaml(self, exclude=None):
        '''Serialize these settings as yaml.'''

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
    data = yaml.safe_dump(DEFAULT_SETTINGS, default_flow_style=False)
    with open(settings_file, 'wb') as f:
        f.write(bytes(data, 'utf-8'))


def find_in_paths(paths, resource):
    '''Find a resource in a list of paths'''

    for path in paths:
        potential_path = unipath(path, resource)
        if os.path.exists(potential_path):
            return potential_path
