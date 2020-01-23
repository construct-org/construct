# -*- coding: utf-8 -*-

from __future__ import absolute_import

# Third party imports
from Qt import QtCore


class TreeNode(object):

    def __init__(self, name, parent=None):
        self._name = name
        self._parent = parent
        self._children = []

        if parent:
            self.parent.addChild(self)


class TreeModel(QtCore.QAbstractItemModel):

    def __init__(self, data, parent=None):
        super(TreeModel, self).__init__(parent)

    def index(self, row, column, parent=QtCore.QModelIndex()):
        pass

    def parent(self, child):
        if not child.isValid():
            return QtCore.QModelIndex()

        # TODO: get parent index
        return QtCore.QModelIndex()

    def rowCount(self, parent=QtCore.QModelIndex()):
        pass

    def columnCount(self, parent=QtCore.QModelIndex()):
        pass

    def data(self, index, role):

        if role == QtCore.Qt.DisplayRole:
            # TODO: text repr
            pass
