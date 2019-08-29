# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import absolute_import
import os
import re
import glob
import logging
import inspect

# Local imports
from ..utils import unipath
from ..ui.scale import pix
from ..compat import wraps, Path


_log = logging.getLogger('construct.ui.resources')

RESOURCE_EXTENSIONS = ['.png', '.ttf', '.css', '.svg', '.gif', '.jpeg']
this_package = Path(__file__).parent


def loads_resources(fn):
    '''A decorator that ensures BuiltinResources is loaded before executing
    the wrapped function.
    '''

    @wraps(fn)
    def call_fn(*args, **kwargs):
        BuiltinResources()._load()
        return fn(*args, **kwargs)
    return call_fn


class ResourceNotFoundError(Exception):
    '''Raised when a resource can not be found.'''


class Resources(object):
    '''Work with resources for an API object.

    Resource Resolution:
        1. Lookup resources starting with ":/" in BuiltinResources
        2. Lookup resources relative to self.api.path
        3. Lookup resources in BuiltinResources
    '''

    def __init__(self, api):
        self.api = api
        self.builtin_resources = BuiltinResources()

    def get(self, resource):
        '''get a resource by relative path.'''

        if resource.startswith(':/'):
            if resource in self.builtin_resources:
                return self.builtin_resources.get(resource)
            else:
                resource = resource.lstrip(':/')

        resource_file = self.api.path.find(resource)
        if resource_file:
            return resource_file

        resource = ':/' + resource
        if resource in self.builtin_resources:
            return self.builtin_resources.get(resource)

        raise ResourceNotFoundError('Could not find resource %s' % resource)

    def ls(self, search=None, extensions=None):
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
        for path in self.api.path:
            for ext in extensions:
                for file in path.glob('*/*' + ext):
                    resource = file.relative_to(path).as_posix().lstrip('./')
                    if search and search not in resource:
                        continue
                    resources.setdefault(resource, file)

        # Combine with BuiltinResources and sort
        bresources = self.builtin_resources.ls(search, extensions)
        return sorted(list(resources.items()) + bresources)

    def style(self, resource):
        '''Get a stylesheet by resource.'''

        style = self.get(resource).read_text(encoding='utf-8')
        return process_stylesheet(style)

    def qicon(self, resource, size=None, color=None):
        '''Get a resource as a QIcon.'''

        return self.builtin_resources.qicon(self.get(resource), size, color)

    def qpixmap(self, resource, size=None, color=None):
        '''Get a resource as a QPixmap.'''

        return self.builtin_resources.qpixmap(self.get(resource), size, color)


class BuiltinResources(object):
    '''Work with builtin resources including icons, branding, stylesheets
    and fonts.
    '''

    _loaded = False
    _font_ids = []
    _resources = {}

    def __init__(self):
        self._update_resources()

    def __contains__(self, resource):
        return resource in self._resources

    def _update_resources(self):
        '''Update BuiltinResources._resources dict.'''

        if self._resources:
            return

        for file in this_package.glob('*/*.*'):

            if file.suffix not in RESOURCE_EXTENSIONS:
                continue

            rel_file = file.relative_to(this_package).as_posix().lstrip('./')
            resource = ':/' + rel_file
            self._resources[resource] = file

    def _load(self):
        '''Loads builtin ui resources'''
        if BuiltinResources._loaded:
            return

        _log.debug('Loading BuiltinResources.')
        from . import _resources

        from Qt import QtGui
        for resource in self._resources.keys():
            if resource.endswith('.ttf'):
                font_id = QtGui.QFontDatabase.addApplicationFont(resource)
                self._font_ids.append(font_id)

        BuiltinResources._loaded = True

    def get(self, resource):
        '''Get a resource's filepath'''

        if resource not in self._resources:
            raise ResourceNotFoundError('Could not find resource: ' + resource)

        return self._resources[resource]

    def ls(self, search=None, extensions=None):
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

    @loads_resources
    def style(self, resource):
        '''Get a stylesheet by name or resource.'''

        style = self.get(resource).read_text(encoding='utf-8')
        return process_stylesheet(style)

    @loads_resources
    def qicon(self, resource, size=None, color=None):
        '''Get a resource as a QIcon.'''

        from Qt import QtGui

        pixmap = self.qpixmap(resource, size, color)
        icon = QtGui.QIcon(pixmap)
        return icon

    @loads_resources
    def qpixmap(self, resource, size=None, color=None):
        '''Get a resource as a QPixmap.'''

        from Qt import QtGui, QtCore

        pixmap = QtGui.QPixmap(str(resource))
        if size:
            pixmap = pixmap.scaled(
                pix(size[0]),
                pix(size[1]),
                mode=QtCore.Qt.SmoothTransformation,
            )
        if color:
            # TODO: Colorize pixmap
            pass
        return pixmap


def process_stylesheet(stylesheet):
    '''Scales all the pixel values in the stylesheet to work with the current
    monitors DPI.
    '''

    pixel_values = re.findall(r'\d+px', stylesheet)
    for pixel_value in pixel_values:
        scaled_value = pix(int(pixel_value[:-2]))
        stylesheet.replace(pixel_value, str(scaled_value) + 'px', 1)

    return stylesheet


def preview_icons(api=None):
    '''Show an icon preview dialog'''

    if api:
        resources = api.resources
    else:
        resources = BuiltinResources()

    from Qt import QtWidgets, QtCore

    app = QtWidgets.QApplication.instance()
    standalone = False

    if not app:
        standalone = True
        app = QtWidgets.QApplication([])

    def icon_widget(resource):
        icon_label = QtWidgets.QLabel()
        icon_label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        icon_label.setPixmap(resources.qpixmap(resource, (24, 24)))
        label = QtWidgets.QLabel(resource)
        label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setStretch(0, 1)
        layout.addWidget(icon_label)
        layout.addWidget(label)
        widget.setLayout(layout)
        return widget

    dialog = QtWidgets.QDialog()
    layout = QtWidgets.QGridLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    columns = 3
    for i, (resource, resource_file) in enumerate(resources.ls('icons')):
        widget = icon_widget(resource)
        col, row = (i % columns), int(i * (1.0 / columns))
        layout.addWidget(widget, row, col)

    dialog.setLayout(layout)
    dialog.setStyleSheet(resources.style(':/styles/light.css'))

    if standalone:
        import sys
        sys.exit(dialog.exec_())
    else:
        dialog.exec_()

