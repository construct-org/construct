# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os

from .utils import unipath
from .constants import DEFAULT_PATHS


class Path(list):

    def __init__(self, path=None):
        self._custom = bool(path)
        if path:
            self.extend(path)

    def load(self):
        if self._custom:
            return
        try:
            env_paths = os.environ['CONSTRUCT_PATH'].strip(os.pathsep)
            self.extend(env_paths.split(os.pathsep))
        except KeyError:
            pass
        self.extend(DEFAULT_PATHS)

    def unload(self):
        self.clear()

    def find(self, resource):
        for path in self:
            potential_path = unipath(path, resource)
            if os.path.exists(potential_path):
                return potential_path
