# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import absolute_import
import logging
import os


_log = logging.getLogger('construct.nuke.callbacks')


def on_script_save():
    '''onScriptSave callback'''

    import nuke
    _log.debug('on_script_save')


def on_script_load():
    '''onScriptLoad callback'''

    import nuke
    _log.debug('on_script_load')


def register():
    '''Register script callbacks'''

    import nuke
    nuke.addOnScriptLoad(on_script_load)
    nuke.addOnScriptSave(on_script_save)


def unregister():
    '''Unregister script callbacks'''

    import nuke
    nuke.removeOnScriptLoad(on_script_load)
    nuke.removeOnScriptSave(on_script_save)
