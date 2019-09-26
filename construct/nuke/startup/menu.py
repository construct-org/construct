# -*- coding: utf-8 -*-

from __future__ import absolute_import

# Standard library imports
import logging

# Third party imports
from nukescripts.utils import executeDeferred

# Local imports
import construct


_log = logging.getLogger('construct.nuke.menu')


def load_construct():
    api = construct.API()
    _log.debug('Construct loaded in The Foundry Nuke.')
    api.host.after_launch(api, api.context.copy())


executeDeferred(load_construct)
