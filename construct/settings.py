# -*- coding: utf-8 -*-
from __future__ import absolute_import
import copy
import os
import shutil
import sys
import logging

from builtins import open, bytes
from past.builtins import basestring
import yaml

from . import schemas
from .compat import wraps
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
        'extensions',
        'icons',
        'templates'
    ]

    def __init__(self, path):
        self.path = path
        self.file = None
        self.folder = None
        self.is_loaded = False
        self._sections = {}

    def add_section(self, name, schema=None):
        section = Section(name, self.folder / name, schema)
        section.load()
        self._sections[name] = section

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            return self._sections[key]

    def load(self):
        v = schemas.get_validator('settings')
        if not v.validate(DEFAULT_SETTINGS):
            raise InvalidSettings(
                'DEFAULT_SETTINGS have the following errors:\n' +
                v.errors_yaml
            )

        self.update(**DEFAULT_SETTINGS)
        self.file = self.path[-1] / SETTINGS_FILE
        potential_settings_file = find_in_paths(self.path, SETTINGS_FILE)

        if potential_settings_file:
            self.file = potential_settings_file
            _log.debug('Loading settings from %s' % self.file)

            # Read settings from file
            data = potential_settings_file.read_bytes().decode('utf-8')
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

        self.folder = self.file.parent

        # Make sure our settings folders exist
        ensure_exists(*[self.folder / f for f in self.structure])

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

            # Write modified settings
            self.file.write_bytes(data)

    def yaml(self, exclude=None):
        '''Serialize these settings as yaml.'''

        settings_to_encode = copy.deepcopy(dict(self))
        exclude = (exclude or [])
        for key in exclude:
            settings_to_encode.pop(key, None)
        return yaml.safe_dump(settings_to_encode, default_flow_style=False)


def load_on_modified(method):
    '''Section method wrapper. Load when mtime changes.'''
    @wraps(method)
    def call_method(self, *args, **kwargs):
        mtime = self.folder.stat().st_mtime
        if self.mtime != mtime:
            self.load()
        return method(self, *args, **kwargs)
    return call_method


class Section(dict):

    def __init__(self, name, folder, schema=None):
        self.name = name
        self.folder = folder
        self.schema = schema
        self.mtime = None
        self.files = {}
        self.load()

    def _get_file(self, name):
        return self.folder / (name + '.yaml')

    def _get_validator(self):
        if not self.schema:
            return

        if isinstance(self.schema, basestring):
            return schemas.get_validator(self.schema)

        if isinstance(self.schema, dict):
            return schemas.new_validator(self.schema)

        raise schemas.SchemaError('Could not load schema: %s' % self.schema)

    def validate(self, data, **kwargs):
        v = self._get_validator()
        if not v:
            return data

        valid_data = v.validated(data, **kwargs)
        if not valid_data:
            raise InvalidSettings(v.errors_yaml)

        return valid_data

    def load(self):
        ensure_exists(self.folder)
        self.mtime = self.folder.stat().st_mtime

        v = self._get_validator()

        section_files = {}
        section_data = {}
        for file in self.folder.iterdir():

            if file.suffix not in ('.yml', '.yaml'):
                continue

            raw_data = file.read_bytes().decode('utf-8')
            data = yaml.load(raw_data)
            try:
                data = self.validate(data)
            except InvalidSettings as e:
                raise InvalidSettings(
                    file + ' contains the following errors:\n' +
                    str(e)
                )

            section_data[file.stem] = data
            section_files[file.stem] = file

        self.clear()
        self.update(section_data)
        self.files.clear()
        self.files.update(section_files)

    def write(self, name, data):
        try:
            data = self.validate(data)
        except InvalidSettings as e:
            raise InvalidSettings(str(e))

        dict.__setitem__(self, name, data)

        yaml_data = yaml.dump(data, default_flow_style=False)

        file = self._get_file(name)
        file.write_bytes(bytes(yaml_data, 'utf-8'))
        return data

    def delete(self, name):
        dict.pop(self, name, None)
        file = self._get_file(name)
        if file.is_file():
            file.unlink()

    # Setup standard dict methods
    __getitem__ = load_on_modified(dict.__getitem__)
    read = __getitem__
    __delitem__ = delete
    pop = delete
    __setitem__ = write
    items = load_on_modified(dict.items)
    keys = load_on_modified(dict.keys)


def restore_default_settings(where):
    '''Create a default configuration in the provided folder.'''

    where = unipath(where)
    if where.is_dir():
        shutil.rmtree(str(where))

    ensure_exists(where)
    ensure_exists(*[where / f for f in Settings.structure])

    settings_file = where / SETTINGS_FILE
    data = yaml.safe_dump(DEFAULT_SETTINGS, default_flow_style=False)

    # Write default settings
    settings_file.write_bytes(bytes(data, 'utf-8'))


def find_in_paths(paths, resource):
    '''Find a resource in a list of paths'''

    for path in paths:
        potential_path = path / resource
        if potential_path.exists():
            return potential_path
