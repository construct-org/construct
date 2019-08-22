# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import absolute_import
import logging

# Third party imports
from nukescripts.utils import executeDeferred

# Local imports
import construct


_log = logging.getLogger('construct.nuke.menu')


def load_construct():
    _log.debug('Loading Construct in The Foundry Nuke.')
    api = construct.API()
    api.host.after_launch(api, api.context.copy())


executeDeferred(load_construct)
