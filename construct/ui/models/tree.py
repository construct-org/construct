# -*- coding: utf-8 -*-

from __future__ import absolute_import

# Third party imports
from Qt import QtCore

# Local imports
from ..theme import theme


class Node(object):

    def __init__(self, data, parent=None):
        self.data = data
        self._parent = parent
        self._children = []

        if parent:
            parent.add_child(self)

    def parent(self):
        return self._parent

    def row(self):
        return self._parent._children.index(self)

    def child(self, row):
        return self._children[row]

    def children(self):
        return self._children

    def add_child(self, node):
        self._children.append(node)

    def insert_child(self, index, child):
        try:
            self._children.insert(index, child)
            child._parent = self
            return True
        except IndexError:
            return False

    def remove_child(self, index):

        try:
            child = self._children.pop(index)
            child._parent = None
            return True
        except IndexError:
            return False

    def child_count(self):
        return len(self._children)


class TreeModel(QtCore.QAbstractItemModel):

    def __init__(self, root, parent=None):
        super(TreeModel, self).__init__(parent)
        self._root = root

    def rowCount(self, parent):
        if not parent.isValid():
            parentNode = self._root
        else:
            parentNode = parent.internalPointer()

        return parentNode.childCount()

    def columnCount(self, parent):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == QtCore.Qt.SizeHintRole:
            return QtCore.QSize(40, 40)

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if index.column() == 0:
                return node.data['name']

        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                theme.icon('square')

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid():

            if role == QtCore.Qt.EditRole:

                node = index.internalPointer()
                node.setName(value)

                return True
        return False

    def parent(self, index):
        node = self.getNode(index)
        parent = node.parent()

        if parent == self._root:
            return QtCore.QModelIndex()

        return self.createIndex(parent.row(), 0, parent)

    def index(self, row, column, parent):
        parent = self.getNode(parent)
        child = parent.child(row)

        if child:
            return self.createIndex(row, column, child)
        else:
            return QtCore.QModelIndex()

    def getNode(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
        return self._root
