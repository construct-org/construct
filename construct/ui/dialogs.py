# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import absolute_import

# Third party imports
from Qt import QtCore, QtWidgets

# Local imports
from .layouts import HBarLayout


class BaseDialog(QtWidgets.QDialog):
    '''Frameless Dialog

    Arguments:
        parent (QObject)
        f (QtCore.Qt.WindowFlags)
    '''

    def __init__(self, *args):
        super(BaseDialog, self).__init__(*args)
