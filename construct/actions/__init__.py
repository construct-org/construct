# -*- coding: utf-8 -*-
from __future__ import absolute_import
from construct.actions.project import NewProject, tag_project_step


def is_available(context):
    return True


def register(cons):
    '''Register all default actions'''

    # Project actions
    cons.action_hub.register(NewProject)
    cons.action_hub.subscribe(NewProject, tag_project_step)


def unregister(cons):
    '''Unregister all default actions'''

    # Project actions
    cons.action_hub.unregister(NewProject)
    cons.action_hub.unsubscribe(NewProject, tag_project_step)

