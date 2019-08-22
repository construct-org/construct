# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import absolute_import
import logging

# Third party imports
from maya.utils import executeDeferred

# Local imports
import construct


_log = logging.getLogger('construct.maya.userSetup')


def load_construct():
    _log.debug('Construct loaded in Autodesk Maya.')
    api = construct.API()
    api.host.after_launch(api, api.context.copy())


executeDeferred(load_construct)
