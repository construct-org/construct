# -*- coding: utf-8 -*-
from __future__ import absolute_import
from construct.core.action import Action


class NewProject(Action):

    label = 'New Project'
    identifier = 'new.project'
    parameters = dict(
        root={
            'label': 'Project Root',
            'required': True,
            'type': str,
            'help': 'project root directory',
        },
    )
    description = 'Create a new Construct project'

    @staticmethod
    def available(context):
        return context.project is None
