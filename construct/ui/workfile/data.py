from __future__ import absolute_import, print_function

from Qt import QtCore, QtGui, QtWidgets, QtCompat, QtSvg
import sys, os, logging, glob

_log = logging.getLogger(__name__)

class getFileBaseModel(object):
    application = [] # ['maya', 'nuke', 'houdini']
    ext = []

    def __init__ ( self, path):
        self._filePath = os.path.normpath( path)
        self._allFiles = []


    # extention for application
    def get_files( self):
        
        temp_store = []

        for i in range( len( self.ext)):
            temp_store.append( glob.glob( os.path.join( self._filePath, i)))

        return temp_store

    def get_tree( self):
        pass

    # getting properties
    def get_task_path( self):
        pass

    # classmethod
    @classmethod
    def set_application( cls, application):
        cls.application = application
        app = cls.application

        if app == "maya":
                cls.ext = ["*.mb", "*.ma"]
        elif app == "nuke":
                cls.ext = ["*.nk"]
        elif app == "houdini":
                cls.ext = ["hip"]
        else:
            cls.ext = ["*.*"]
        return cls.ext

popo = getFileBaseModel( r'Z:\Active_Projects\19_051_waymo\production\shots\SQ010_Previs\SQ010_PREVIS_SH030\layout\work\maya')
popo.set_application( "nuke")
print ( popo.get_files())
# popo.application = 'maya'
#for i in popo.get_allFiles():
#    print (i)