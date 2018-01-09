# -*- coding: utf-8 -*-
from __future__ import absolute_import
from construct.actions.project import NewProject


def available(context):
    return True


def register(cons):
    '''Register all default actions'''

    # Project actions
    cons.action_hub.register(NewProject)


def unregister(cons):
    '''Unregister all default actions'''

    # Project actions
    cons.action_hub.unregister(NewProject)

