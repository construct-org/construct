# -*- coding: utf-8 -*-
import os

from .utils import unipath
from .constants import DEFAULT_PATHS


class Path(list):

    def load(self):
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
