# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function

# Standard library imports
import logging
import os
import re


_log = logging.getLogger('construct.hou.callbacks')


def set_context_to_hou_scene():
    '''Sets the Context to the current houd scene, if it's in a workspace'''
    _log.debug('Setting Construct context from Houdini Scene.')


def scene_event_callback(event_type):
    '''Scene event callback'''

    import hou

    accepted_events = (
        hou.hipFileEventType.AfterLoad,
        hou.hipFileEventType.AfterSave,
    )
    if event_type in accepted_events:
        set_context_to_hou_scene()


def register():
    '''Register construct_hou callbacks'''

    import hou
    hou.hipFile.addEventCallback(scene_event_callback)


def unregister():
    '''Register construct_hou callbacks'''

    import hou
    hou.hipFile.addEventCallback(scene_event_callback)
