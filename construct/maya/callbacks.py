# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import absolute_import, print_function
import os
import re
import logging
import glob

# Local imports
from ..utils import unipath


_log = logging.getLogger('construct.maya.callbacks')
_callback_ids = []


def after_open(*args):
    '''kAfterOpen callback'''

    _log.debug('after_open')
    # TODO: Set the construct context and maya workspace based on the
    # opened file.


def after_save(*args):
    '''kAfterSave callback'''

    _log.debug('after_open')
    # TODO: Set the construct context and maya workspace based on the
    # saved file.


def before_create_reference_check(mfile, client_data):
    '''kBeforeCreateReferenceCheck callback'''

    _log.debug('before_create_reference_check')
    # TODO: make sure that the referenced file is the latest version
    # of a publish. If it is not, prompt user to update.
    return True


def register():
    '''Register scene callbacks'''

    from maya.api import OpenMaya
    MSceneMessage = OpenMaya.MSceneMessage

    after_open_id = MSceneMessage.addCallback(
        MSceneMessage.kAfterOpen,
        after_open
    )
    _callback_ids.append(after_open_id)

    after_save_id = MSceneMessage.addCallback(
        MSceneMessage.kAfterSave,
        after_save
    )
    _callback_ids.append(after_save_id)

    before_create_reference_check_id = MSceneMessage.addCheckFileCallback(
        MSceneMessage.kBeforeCreateReferenceCheck,
        before_create_reference_check
    )
    _callback_ids.append(before_create_reference_check_id)


def unregister():
    '''Unregister scene callbacks'''

    from maya.api import OpenMaya

    while _callback_ids:
        _id = _callback_ids.pop()
        OpenMaya.MMessage.removeCallback(_id)
