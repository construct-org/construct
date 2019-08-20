# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import re
import glob
import logging

from ..utils import unipath
from ..ui.scale import pix


_log = logging.getLogger('construct.ui.resources')
_initialized = False
_font_ids = []

EXTENSIONS = ['', '.png', '.ttf', '.css']
THIS_PATH = unipath(os.path.dirname(__file__))


def load():
    '''Load compiled qt resources and add application fonts.'''

    global _initialized
    if _initialized:
        return

    # Load built resources
    from . import _resources

    # Load fonts
    from Qt import QtGui
    for resource, resource_file in ls('fonts'):
        font_id = QtGui.QFontDatabase.addApplicationFont(resource)
        _font_ids.append(font_id)

    _initialized = True


def unload():
    # TODO: we could unload fonts here, but should we bother?
    pass


class ResourceNotFoundError(Exception):
    '''Raised when a resource can not be found.'''
    pass


def path(resource):
    '''Get a resources filepath'''

    resource_file = THIS_PATH / resource.lstrip(':/')

    if not resource_file.is_file():
        raise ResourceNotFoundError('Could not find resource: ' + resource)

    return resource_file


def ls(search=None):
    '''List all resources

    Returns:
        List of tuples - (resource, resource_file)
    '''
    resources = []

    for file in THIS_PATH.glob('*/*.*'):

        if file.suffix not in EXTENSIONS:
            continue

        if search and search not in file.as_posix():
            continue

        resource = ':/' + file.relative_to(THIS_PATH).as_posix().lstrip('./')
        resources.append((resource, file.as_posix()))

    return resources


def read(resource):
    '''Read a resource'''

    resource_path = path(resource)
    with open(resource_path, 'r') as f:
        return f.read()


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
    dialog.setStyleSheet(style('dark'))

    if standalone:
        dialog.exec_()

