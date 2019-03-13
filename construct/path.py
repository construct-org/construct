# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os

from builtins import super
from .utils import unipath
from .constants import DEFAULT_PATHS


class Path(list):
    '''A list of folders used to lookup resources like settings, icons, and
    extensions.
    '''

    def __init__(self, path=None):
        super().__init__()
        self._custom = bool(path)
        self._custom_path = path

    def load(self):
        if self._custom:
            self.extend(self._custom_path)
            return
        try:
            env_paths = os.environ['CONSTRUCT_PATH'].strip(os.pathsep)
            self.extend(env_paths.split(os.pathsep))
        except KeyError:
            pass
        self.extend(DEFAULT_PATHS)

    def unload(self):
        self[:] = []

    def find(self, resource):
        '''Find a resource in one of this objects paths.

        Examples:
            >>> path = Path(['~/.construct'])
            >>> path.find('construct.yaml')
            '~/.construct/construct.yaml'
        '''
        for path in self:
            potential_path = unipath(path, resource)
            if os.path.exists(potential_path):
                return potential_path
