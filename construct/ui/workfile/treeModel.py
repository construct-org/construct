from __future__ import absolute_import, print_function

from Qt import QtCore, QtGui, QtWidgets, QtCompat, QtSvg
import sys, os, logging

_log = logging.getLogger(__name__)

class Node(object):
    
    def __init__(self, name, parent=None):
        
        self._name = name
        self._children = []
        self._parent = parent
        
        if parent is not None:
            parent.addChild(self)

    def typeInfo(self):
        return "None"

    def addChild(self, child):
        self._children.append(child)

    def insertChild(self, position, child):
        
        if position < 0 or position > len(self._children):
            return False
        
        self._children.insert(position, child)
        child._parent = self
        return True

    def removeChild(self, position):
        
        if position < 0 or position > len(self._children):
            return False
        
        child = self._children.pop(position)
        child._parent = None

        return True

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name

    def child(self, row):
        return self._children[row]
    
    def childCount(self):
        return len(self._children)

    def parent(self):
        return self._parent
    
    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)

class SubProjectNode(Node):
    
    def __init__(self, name, parent=None):
        super(SubProjectNode, self).__init__(name, parent)
        
    def typeInfo(self):
        return "SUBPROJECT"

class Level01Node(Node):
    
    def __init__(self, name, parent=None):
        super(Level01Node, self).__init__(name, parent)
        
    def typeInfo(self):
        return "LEVEL01"

class Level02Node(Node):
    
    def __init__(self, name, parent=None):
        super(Level02Node, self).__init__(name, parent)
        
    def typeInfo(self):
        return "LEVEL02"


class Level03Node(Node):
    
    def __init__(self, name, parent=None):
        super(Level03Node, self).__init__(name, parent)

    def typeInfo(self):
        return "LEVEL03"


class taskTreeModel(QtCore.QAbstractItemModel):
    
    def __init__(self, root, parent=None):
        super(taskTreeModel, self).__init__(parent)
        self._rootNode = root

    def rowCount(self, parent):
        if not parent.isValid():
            parentNode = self._rootNode
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
                return node.name()
            
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                typeInfo = node.typeInfo()
                
                if typeInfo == "SUBPROJECT":
                    return QtGui.QIcon(QtGui.QPixmap(":/subproject.png"))
                
                if typeInfo == "LEVEL01":
                    return QtGui.QIcon(QtGui.QPixmap(":/level01.png"))
                
                if typeInfo == "LEVEL02":
                    return QtGui.QIcon(QtGui.QPixmap(":/level02.png"))
                
                if typeInfo == "LEVEL03":
                    return QtGui.QIcon(QtGui.QPixmap(":/level03.png"))

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid():
            
            if role == QtCore.Qt.EditRole:
                
                node = index.internalPointer()
                node.setName(value)
                
                return True
        return False

    def parent(self, index):
        node = self.getNode(index)
        parentNode = node.parent()
        
        if parentNode == self._rootNode:
            return QtCore.QModelIndex()
        
        return self.createIndex(parentNode.row(), 0, parentNode)

    def index(self, row, column, parent):
        parentNode = self.getNode(parent)
        childItem = parentNode.child(row)

        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def getNode(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
            
        return self._rootNode
