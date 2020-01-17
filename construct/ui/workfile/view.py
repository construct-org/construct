from __future__ import absolute_import, print_function

import sys, os, re
import logging

# Third party imports
from Qt import QtCore, QtGui, QtWidgets, QtCompat, QtSvg
from functools import partial


# import motules
from ..dialogs import FramelessDialog
from ..layouts import BarLayout
from .resources.openDialog import Ui_Form

_log = logging.getLogger(__name__)

class workfile(QtWidgets.QWidget, Ui_Form):

    def __init__ (self, parent = None):
        QtWidgets.QWidget.__init__( self, parent)
        self.setupUi(self)


        # Setup UI
        self.treeView.setHeaderHidden(True)
        self.treeView_2.setHeaderHidden(True)
        self.splitter.setSizes( [self.width()/8.5, self.height()])

        # All Widget connections will be here
        self.pushButton_3.clicked.connect( partial( self.list_icon))
        self.listView.clicked.connect( partial( self.itemClicked))


    # Widget functions
    def itemClicked(self, model_index):
        model_dict = self.listView.model().itemData(model_index)
        print( str( model_dict.get(0)))
        return model_dict.get(0)

    def list_icon( self):
        if "Icon" not in str( self.listView.viewMode()):
            self.listView.setFlow(QtWidgets.QListView.LeftToRight)
            self.listView.setGridSize(QtCore.QSize(120, 50))
            self.listView.setViewMode(QtWidgets.QListView.IconMode)
        
        else:
            self.listView.setFlow(QtWidgets.QListView.TopToBottom)
            self.listView.setGridSize(QtCore.QSize(-1, -1))
            self.listView.setViewMode(QtWidgets.QListView.ListMode)
