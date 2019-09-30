# -*- coding: utf-8 -*-

from __future__ import absolute_import

# Standard library imports
import copy
import logging
import os
import shutil
import sys

# Local imports
from . import schemas
from .compat import basestring, wraps
from .constants import (
    DEFAULT_SETTINGS,
    SETTINGS_FILE,
    USER_PATH,
    USER_SETTINGS_FILE,
)
from .errors import InvalidSettings, ValidationError
from .utils import ensure_exists, unipath, yaml_dump, yaml_load


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
            data = potential_settings_file.read_text(encoding='utf-8')
            if data:
                file_data = yaml_load(data)
            else:
                file_data = {}

            if not v.validate(file_data):
                raise InvalidSettings(
                    str(self.file) + ' contains the following errors:\n' +
                    v.errors_yaml
                )

            self.update(**file_data)
        else:
            _log.debug(
                'Settings file not found.'
                ' Writing default settings to ' + str(self.file)
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
            data = self.yaml(exclude=['software'])

            # Write modified settings
            self.file.write_bytes(data)

    def yaml(self, exclude=None):
        '''Serialize these settings as yaml.'''

        settings_to_encode = copy.deepcopy(dict(self))
        exclude = (exclude or [])
        for key in exclude:
            settings_to_encode.pop(key, None)
        return yaml_dump(settings_to_encode)


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
            raise ValidationError(
                '%s Section: Data is invalid.\n%s'
                % (self.name, v.errors_yaml),
                errors=v.errors
            )

        return valid_data

    def load(self):
        ensure_exists(self.folder)
        self.mtime = self.folder.stat().st_mtime

        section_files = {}
        section_data = {}
        for file in self.folder.iterdir():

            if file.suffix not in ('.yml', '.yaml'):
                continue

            raw_data = file.read_text(encoding='utf-8')
            data = self.validate(yaml_load(raw_data))

            section_data[file.stem] = data
            section_files[file.stem] = file

        self.clear()
        self.update(section_data)
        self.files.clear()
        self.files.update(section_files)

    def write(self, name, data):
        data = self.validate(data)
        dict.__setitem__(self, name, data)

        file = self._get_file(name)
        file.write_bytes(yaml_dump(data))
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

    # Write default settings
    settings_file = where / SETTINGS_FILE
    settings_file.write_bytes(yaml_dump(DEFAULT_SETTINGS))


def find_in_paths(paths, resource):
    '''Find a resource in a list of paths'''

    for path in paths:
        potential_path = path / resource
        if potential_path.exists():
            return potential_path