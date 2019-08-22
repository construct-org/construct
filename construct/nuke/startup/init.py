# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import absolute_import
import logging

# Local imports
import construct


_log = logging.getLogger('construct.nuke.init')
_log.debug('Initializing Nuke.')
api = construct.API()
