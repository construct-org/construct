# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import sys, os, glob
import construct

from Qt import QtWidgets
from construct.ui import dialogs, layouts
from construct.ui.workfile import view, listModel, treeModel

if __name__ == '__main__':

    ### This is a test propose ###
    app = QtWidgets.QApplication(sys.argv)
    aa = view.workfile()

    ### List View ###
    # for for the listview
    pyfile = [os.path.split( x)[1] for x in glob.glob( r"Z:\Active_Projects\19_051_waymo\production\shots\SQ010_Previs\SQ010_PREVIS_SH030\layout\work\maya\*.mb")]
    pyfile.sort()
    pyfile.reverse()

    # The icons and file extension will vary depending on application (application = 'maya', 'nuke', 'houdini')
    itemList = listModel.ListModel( pyfile, application = 'nuke')

    # set model to listview
    aa.listView.setModel( itemList)

    ### Tree View ###
    # Treeview for asset level
    rootAssetNode   = treeModel.Node("root")
    projectNode = treeModel.SubProjectNode("Sub-Project", rootAssetNode)
    childNode00 = treeModel.Level01Node("Characters", projectNode)
    childNode01 = treeModel.Level01Node("Envieonment", projectNode)
    
    tasks = ["Model", "Anim", "Lighting", "Texture"]

    # children nodes for assets
    assets = ["Man_A", "Man_B", "Man_C"]
    
    for i in assets:
        _temp = treeModel.Level02Node( i, childNode00)
        for j in tasks:
            treeModel.Level03Node( j, _temp)

    # Treeview for shot level
    rootShotNode   = treeModel.Node("root")
    projectNode = treeModel.SubProjectNode("Sub-Project", rootShotNode)
    
    tasks = ["Anim", "Lighting", "Comp", "Texture"]

    # children nodes for shots
    shots = ["SH010", "SH020", "SH030"]
    
    for i in shots:
        _temp = treeModel.Level01Node( i, projectNode)
        for j in tasks:
            treeModel.Level02Node( j, _temp)

    # make nodes to Model data set
    treeViewModel = treeModel.taskTreeModel(rootAssetNode)
    treeViewModel1 = treeModel.taskTreeModel(rootShotNode)

    # assign data to treeViews 
    aa.treeView.setModel( treeViewModel)
    aa.treeView_2.setModel( treeViewModel1)

    aa.show()
    sys.exit(app.exec_())