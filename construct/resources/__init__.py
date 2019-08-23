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

RESOURCE_EXTENSIONS = ['', '.png', '.ttf', '.css']
this_package = Path(__file__).parent


def ensure_resources_loaded(fn):
    '''A decorator that executes callables that have been marked lazy using
    the lazy function.
    '''
    @wraps(method)
    def call_fn(*args, **kwargs):
        load_qt_resources()
        return call_fn(*args, **kwargs):
    return call_fn


class ResourceNotFoundError(Exception):
    '''Raised when a resource can not be found.'''


class Resources(object):
    '''Resources object. Looks up builtin qt resources as well as user
    resources stored in a users CONSTRUCT_PATH.'''

    _qresources_loaded = False
    _font_ids = []

    def load(self):
        pass

    def unload(self):
        pass

    def find(self, resource):
        try:
            return find(resource)
        except ResourceNotFoundError:
            return self.api.path.find(resources.lstrip(':/'))

    def ls(self, search=None):

        builtin_resources = ls(search)
        user_resources = []

        for path in self.api.path:
            user_resources.extend(ls(search, path=path))

        return builtin_resources + user_resources

    def read(self, resource):
        '''Read a resource'''

        return self.find(resource).read_text(encoding='utf-8')

    @ensure_resources_loaded
    def style(self, name_or_resource):
        '''Get a stylesheet from a name or resource.'''

        if name_or_resource.startswith(':/'):
            resource = name_or_resource
        else:
            resource = ':/css/' + name_or_resource + '.css'
        style = self.read(resource)

        pixel_values = re.findall(r'\d+px', style)
        for pixel_value in pixel_values:
            scaled_value = pix(int(pixel_value[:-2]))
            style.replace(pixel_value, str(scaled_value) + 'px', 1)

        return style

    @ensure_resources_loaded
    def icon(resource, size=None, color=None):
        '''Get a resource as a QIcon'''
        pass

    @ensure_resources_loaded
    def pixmap(resource, size=None, color=None):
        '''Get a resource as a QPixmap'''
        pass


def load():
    if Resources._qresources_loaded:
        return

    _log.debug('Loading Qt resources.')
    from . import _resources

    _log.debug('Loading fonts.')
    from Qt import QtGui
    for resource, resource_file in ls('fonts'):
        font_id = QtGui.QFontDatabase.addApplicationFont(resource)
        Resources._font_ids.append(font_id)

    Resources._qresources_loaded = True


def find(resource):
    '''Get a resources filepath'''

    resource_file = this_package / resource.lstrip(':/')

    if not resource_file.is_file():
        raise ResourceNotFoundError('Could not find resource: ' + resource)

    return resource_file


def ls(search=None, path=None, extensions=RESOURCE_EXTENSIONS):
    '''List all resources.

    Arguments:
        search (str): String to search for
        path (Path): Directory to search for resources

    Returns:
        List of tuples - (resource, resource_file)
    '''
    path = path or this_package
    resources = {}

    for file in path.glob('*/*.*'):

        if file.suffix not in extensions:
            continue

        if search and search not in file.as_posix():
            continue

        resource = ':/' + file.relative_to(path).as_posix().lstrip('./')
        resources[resource] = file.as_posix()

    return resources


def read(resource):
    '''Read a resource'''

    return path(resource).read_text(encoding='utf-8')


def style(name_or_resource):
    '''Get a stylesheet from a name or resource.'''

    if name_or_resource.startswith(':/'):
        resource = name_or_resource
    else:
        resource = ':/css/' + name_or_resource + '.css'
    style = read(resource)

    pixel_values = re.findall(r'\d+px', style)
    for pixel_value in pixel_values:
        scaled_value = pix(int(pixel_value[:-2]))
        style.replace(pixel_value, str(scaled_value) + 'px', 1)

    return style


def icon(resource, size=None, color=None):
    '''Get a resource as a QIcon'''

    pixmap = qpixmap(resource, size, color)
    icon = QtGui.QIcon(pixmap)
    return icon


def pixmap(resource, size=None, color=None):
    '''Get a resource as a QPixmap'''

    from Qt import QtGui, QtCore

    pixmap = QtGui.QPixmap(resource)
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


def preview_icons():
    '''Show an icon preview dialog'''

    from Qt import QtWidgets, QtCore

    app = QtWidgets.QApplication.instance()
    standalone = False
    if not app:
        standalone = True
        app = QtWidgets.QApplication([])
        load()

    def icon_widget(resource):
        icon_label = QtWidgets.QLabel()
        icon_label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        icon_label.setPixmap(pixmap(resource, (24, 24)))
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
    for i, (resource, resource_file) in enumerate(ls('icons')):
        widget = icon_widget(resource)
        col, row = (i % columns), int(i * (1.0 / columns))
        layout.addWidget(widget, row, col)

    dialog.setLayout(layout)
    dialog.setStyleSheet(style('light'))

    if standalone:
        sys.exit(dialog.exec_())
    else:
        dialog.exec_()

