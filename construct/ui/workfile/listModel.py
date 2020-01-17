from __future__ import absolute_import, print_function

from Qt import QtCore, QtGui, QtWidgets, QtCompat, QtSvg
import sys, os, logging

from . import icon_rc

_log = logging.getLogger(__name__)

class ListModel(QtCore.QAbstractListModel):

    # application = []

    def __init__ (self, files = [], application='default', parent = None):
        QtCore.QAbstractListModel.__init__( self, parent)
        self.__files = files
        self.application = application
        self.icon_init( self.application)

    def rowCount(self, parent):
        return len(self.__files)

    # icon and name
    def data(self, index, role):

        if role == QtCore.Qt.DisplayRole:
            value = str( self.__files[index.row()] );
            return value

        if role == QtCore.Qt.DecorationRole:
            row = index.row()
            value = self.__files[row]
            icon = QtGui.QIcon( self.__icon)
            return icon

    def icon_init ( self, application):

        # Set file icon depending on application
        if application == "maya":
            self.__icon = ":/maya.png"

        elif application == "nuke":
            self.__icon = ":/nuke.png"

        elif application == "houdini":
            self.__icon = ":/houdini.png"
        else:
            self.__icon = ":/subproject.png"
