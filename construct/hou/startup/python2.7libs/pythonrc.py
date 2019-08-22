# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import absolute_import
import logging

# Third party imports
from hdefereval import executeDeferred

# Local imports
import construct


_log = logging.getLogger('construct.hou.pythonrc')


def load_construct():
    api = construct.API()
    _log.debug('Construct loaded in SideFX Houdini.')
    api.host.after_launch(api, api.context.copy())


executeDeferred(load_construct)
