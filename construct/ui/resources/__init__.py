# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import absolute_import
import os
import re
import glob
import logging
import inspect
import json

# Third party imports
from six import reraise

# Local imports
from ...utils import unipath
from ...compat import wraps, Path


_log = logging.getLogger('construct.ui.resources')

IMAGE_EXTENSIONS = [
    '.bmp',
    '.gif',
    '.jpg',
    '.jpeg',
    '.png',
    '.pbm',
    '.pgm',
    '.ppm',
    '.xbm',
    '.xpm',
    '.svg',
]
RESOURCE_EXTENSIONS = IMAGE_EXTENSIONS + [
    '.ttf',
    '.scss',
    '.css',
]
package_path = Path(__file__).parent.resolve()
missing = object()


class ResourceNotFoundError(Exception):
    '''Raised when a resource can not be found.'''


class Resources(object):
    '''Work with resources for an API object.

    Arguments:
        lookup_paths (Path): A list of Path objects usually provided by an API

    Resource Resolution:
        1. Lookup resources relative to lookup_paths
        2. Lookup resources in BuiltinResources
    '''

    font_ids = {}
    font_charmaps = {}
    image_extensions = IMAGE_EXTENSIONS
    resource_extensions = RESOURCE_EXTENSIONS

    def __init__(self, lookup_paths=None):
        self.lookup_paths = lookup_paths or []
        self.builtin_resources = BuiltinResources()
        self.loaded = False
        self.path = package_path

    def load(self):
        if self.loaded:
            return

        from Qt.QtGui import QFontDatabase

        # Load fonts and charmaps
        for resource, font in self.find(extensions=['.ttf']):

            if font.name in self.font_ids:
                continue

            font_id = QFontDatabase.addApplicationFont(font.as_posix())
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            self.font_ids[font.name] = font_id

            # Look for charmaps
            charmap = Path(str(font).replace('.ttf', '_charmap.json'))
            if not charmap.is_file():
                continue

            charmap_data = json.loads(charmap.read_text())
            for family in font_families:
                self.font_charmaps[family] = charmap_data

        self.loaded = True

    def get(self, resource, default=missing):
        '''get a resource by relative path.'''

        for path in self.lookup_paths:
            potential_path = path / resource
            if potential_path.exists():
                return potential_path

        return self.builtin_resources.get(resource, default)

    def get_char(self, char, family=None):
        family = family or 'construct'
        try:
            return self.font_charmaps[family][char]
        except KeyError:
            raise ResourceNotFoundError(
                'Could not find char: %s in font family %s' % (char, family)
            )

    def find(self, search=None, extensions=None):
        '''List all resources.

        Arguments:
            search (str): String to match in resource names
            extensions (List[str]): List of extensions to match

        Returns:
            List of tuples - (resource, resource_file)
        '''

        # Get resources on api.path
        extensions = extensions or RESOURCE_EXTENSIONS
        resources = {}
        for path in self.lookup_paths:
            for ext in extensions:
                for file in path.glob('*/*' + ext):
                    resource = file.relative_to(path).as_posix().lstrip('./')
                    if search and search not in resource:
                        continue
                    resources.setdefault(resource, file)

        # Combine with BuiltinResources and sort
        bresources = self.builtin_resources.find(search, extensions)
        return sorted(list(resources.items()) + bresources)


class BuiltinResources(object):
    '''Work with builtin resources including icons, branding, stylesheets
    and fonts.
    '''

    _resources = {}

    def __init__(self):
        self._update_resources()

    def __contains__(self, resource):
        return resource in self._resources

    def _update_resources(self):
        '''Update BuiltinResources._resources dict.'''

        if self._resources:
            return

        for file in package_path.glob('*/*.*'):

            if file.suffix not in RESOURCE_EXTENSIONS:
                continue

            rel_file = file.relative_to(package_path).as_posix().lstrip('./')
            self._resources[rel_file] = file

    def get(self, resource, default=missing):
        '''Get a resource's filepath'''

        if resource not in self._resources:
            if default is not missing:
                return default
            raise ResourceNotFoundError('Could not find resource: ' + resource)

        return self._resources[resource]

    def find(self, search=None, extensions=None):
        '''List all resources.

        Arguments:
            search (str): String to match in resource names
            extensions (List[str]): List of extensions to match

        Returns:
            List of tuples - (resource, resource_file)
        '''

        resources = []
        for resource, resource_file in self._resources.items():
            if search and search not in resource:
                continue
            if extensions and resource_file.suffix not in extensions:
                continue
            resources.append((resource, resource_file))
        return sorted(resources)
