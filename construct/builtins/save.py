# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import fsfs
from construct.action import Action


class Save(Action):

    label = 'Save'
    identifier = 'save'
    description = 'Save the current file'
    parameters = dict(
        task={
            'label': 'Task',
            'required': True,
            'type': fsfs.Entry,
            'help': 'Task',
        },
        workspace={
            'label': 'Workspace',
            'required': False,
            'type': fsfs.Entry,
            'help': 'Workspace'
        },
        suffix={
            'label': 'Suffix',
            'required': False,
            'type': str,
            'help': 'Filename Suffix',
        },
        version={
            'label': 'Version',
            'required': True,
            'type': int,
            'help': 'File Version'
        }
    )

    @staticmethod
    def available(ctx):
        return ctx.project and ctx.host not in ['cli']
