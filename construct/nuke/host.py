# -*- coding: utf-8 -*-

from __future__ import absolute_import

# Standard library imports
import os
from collections import namedtuple
from os.path import basename

# Local imports
from .. import API
from ..compat import Path
from ..extensions import Host
from ..utils import copy_file, update_env


__all__ = ['Nuke']
package_path = Path(__file__).parent.resolve()
Version = namedtuple('Version', 'major minor patch')


class Nuke(Host):
    '''Construct Nuke Host Extension'''

    identifier = 'nuke'
    label = 'The Foundry Nuke'
    icon = 'icons/nuke.png'

    def load(self, api):
        api.path.append(package_path)
        for software_config in package_path.glob('software/*.yaml'):
            if software_config.stem not in api.software:
                copy_file(software_config, api.software.folder)

    def unload(self, api):
        pass

    @property
    def version(self):
        import nuke
        major = nuke.NUKE_VERSION_MAJOR
        minor = nuke.NUKE_VERSION_MINOR
        patch = nuke.NUKE_VERSION_RELEASE
        return Version(major, minor, patch)

    def modified(self):
        import nuke
        return (
            nuke.root().modified() and
            self.get_filename() != 'Root'
        )

    def save_file(self, file):
        import nuke
        nuke.scriptSaveAs(file)

    def open_file(self, file):
        import nuke
        nuke.scriptOpen(file)

    def get_selection(self):
        import nuke
        return nuke.selectedNodes()

    def set_selection(self, selection):
        for node in self.get_selection():
            node.setSelected(False)
        for node in selection:
            node.setSelected(True)

    def get_workspace(self):
        import nuke
        return nuke.root()['project_directory'].getValue()

    def set_workspace(self, directory):
        import nuke

        fav_icon = self.api.ui.resources.get(
            'brand/construct_icon-white-on-black.png'
        )
        nuke.removeFavoriteDir('project')
        nuke.removeFavoriteDir('asset')
        nuke.removeFavoriteDir('workspace')
        nuke.addFavoriteDir(
            fav_name,
            directory=directory,
            type=(nuke.IMAGE | nuke.SCRIPT | nuke.GEO),
            icon=fav_icon,
            tooltip=directory
        )

        os.chdir(directory)
        nuke.root()['project_directory'].setValue(directory)

    def get_filepath(self):
        import nuke
        return nuke.root().name()

    def get_filename(self):
        import nuke
        return basename(nuke.root().name())

    def get_frame_range(self):
        import nuke
        viewer = nuke.activeViewer().node()
        viewer_range = viewer.knob('frame_range').getValue()
        start, end = [int(v) for v in viewer_range.split('-')]
        root = nuke.root()
        min = root.firstFrame()
        max = root.lastFrame()
        return min, start, end, max

    def set_frame_range(self, min, start, end, max):
        import nuke
        root = nuke.root()
        root.knob('first_frame').setValue(min)
        root.knob('last_frame').setValue(max)
        viewer = nuke.activeViewer().node()
        viewer['frame_range'].setValue('%d-%d' % (start, end))
        viewer['frame_range_lock'].setValue(True)

    def get_frame_rate(self):
        import nuke
        root = nuke.root()
        return root.knob('fps').getValue()

    def set_frame_rate(self, fps):
        import nuke
        root = nuke.root()
        return root.knob('fps').setValue(fps)

    def get_qt_parent(self):
        from Qt import QtWidgets
        app = QtWidgets.QApplication.instance()

        for widget in app.topLevelWidgets():
            if isinstance(widget, QtWidgets.QMainWindow):
                return widget

    def before_launch(self, api, software, env, ctx):
        startup_path = (package_path / 'startup').as_posix()
        update_env(
            env,
            NUKE_PATH=[startup_path],
        )

    def after_launch(self, api, ctx):
        from . import callbacks
        callbacks.register()
