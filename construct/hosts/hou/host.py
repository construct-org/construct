# -*- coding: utf-8 -*-

from __future__ import absolute_import

# Standard library imports
from collections import namedtuple
from os.path import basename, isfile

# Local imports
from ...compat import Path
from ...extensions import Host
from ...utils import copy_file, update_env


__all__ = ['Houdini']
package_path = Path(__file__).parent.resolve()
Version = namedtuple('Version', 'major minor patch')


class Houdini(Host):
    '''Construct Houdini integration'''

    identifier = 'houdini'
    label = 'SideFX Houdini'
    icon = 'icons/houdini.png'

    def load(self, api):
        api.path.append(package_path)
        for software_config in package_path.glob('software/*.yaml'):
            if software_config.stem not in api.software:
                copy_file(software_config, api.software.folder)

    def unload(self, api):
        pass

    @property
    def version(self):
        import hou
        return Version(hou.applicationVersion())

    def modified(self):
        import hou
        return (
            hou.hipFile.hasUnsavedChanges() and
            isfile(self.get_filename())
        )

    def save_file(self, file):
        import hou

        hou.hipFile.save(file)

    def open_file(self, file):
        import hou
        from construct.ui.dialogs import ask

        if self.modified():
            if ask('Would you like to save?', title='Unsaved changes'):
                hou.hipFile.save()

        hou.hipFile.load(file, suppress_save_prompt=True)

    def get_selection(self):
        import hou
        return hou.selectedNodes()

    def set_selection(self, selection):
        for node in self.get_selection():
            node.setSelected(False)
        for node in selection:
            node.setSelected(True)

    def get_workspace(self):
        import os
        return os.environ['JOB']

    def set_workspace(self, directory):
        import os
        os.environ['JOB'] = directory

    def get_filepath(self):
        import hou
        return hou.hipFile.path()

    def get_filename(self):
        import hou
        return basename(hou.hipFile.path())

    def get_frame_range(self):
        import hou
        if self.version > 15:
            min, max = hou.playbar.frameRange()
            start, end = hou.playbar.playbackRange()
        else:
            min, max = hou.playbar.timelineRange()
            start = min
            end = max
        return min, start, end, max

    def set_frame_range(self, min, start, end, max):
        import hou
        if self.version > 15:
            hou.playbar.setFrameRange(min, max)
            hou.playbar.setPlaybackRange(start, end)
        else:
            hou.setPlaybackRange(min, max)

    def get_frame_rate(self):
        import hou
        return hou.fps()

    def set_frame_rate(self, fps):
        import hou
        hou.setFps(fps)

    def get_qt_parent(self):
        import hou
        if self.version.major > 15:
            return hou.qt.mainWindow()
        else:
            return hou.ui.mainQtWindow()

    def before_launch(self, api, software, env, ctx):

        startup_path = (package_path / 'startup').as_posix()
        update_env(
            env,
            HOUDINI_PATH=[startup_path, '&'],
        )

    def after_launch(self, api, ctx):
        from . import callbacks
        callbacks.register()
