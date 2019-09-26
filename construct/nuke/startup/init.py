# -*- coding: utf-8 -*-

from __future__ import absolute_import

# Standard library imports
import logging

# Local imports
import construct


_log = logging.getLogger('construct.nuke.init')
_log.debug('Initializing Nuke.')
api = construct.API()
