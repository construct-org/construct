# -*- coding: utf-8 -*-
from __future__ import absolute_import
from construct.action import Action
from construct import types


class Publish(Action):
    '''Publish the current open file'''

    label = 'Publish'
    identifier = 'publish'

    @staticmethod
    def parameters(ctx):
        params = dict(
            task={
                'label': 'Task',
                'required': True,
                'type': types.Entry,
                'help': 'Task Entry',
            },
            version={
                'label': 'Version',
                'required': True,
                'type': types.Integer,
                'help': 'File Version'
            },
            name={
                'label': 'Name',
                'required': True,
                'type': types.String,
                'help': 'Publish Name'
            }
        )

        # TODO: Implement contextual defaults and options
        return params

    @staticmethod
    def available(ctx):
        return ctx.host != 'cli' and ctx.task


class PublishFile(Action):
    '''Publish a file to the specified task'''

    label = 'Publish File'
    identifier = 'publish.file'

    @staticmethod
    def parameters(ctx):
        params = dict(
            task={
                'label': 'Task',
                'required': True,
                'type': types.Entry,
                'help': 'Task',
            },
            version={
                'label': 'Version',
                'required': True,
                'type': types.Integer,
                'help': 'File Version'
            },
            file={
                'label': 'File path',
                'required': True,
                'type': types.String,
                'help': 'Path to file you want to publish'
            }
        )

        # TODO: Implement contextual defaults and options
        return params

    @staticmethod
    def available(ctx):
        return ctx.host == 'cli' and ctx.task


class Save(Action):
    '''Save the current file'''

    label = 'Save'
    identifier = 'file.save'
    parameters = dict(
        task={
            'label': 'Task',
            'required': True,
            'type': types.Entry,
            'help': 'Task',
        },
        workspace={
            'label': 'Workspace',
            'required': False,
            'type': types.Entry,
            'help': 'Workspace to save to'
        },
        name={
            'label': 'Name',
            'required': False,
            'type': types.String,
            'help': 'Filename',
        },
        version={
            'label': 'Version',
            'required': True,
            'type': types.Integer,
            'help': 'File Version'
        }
    )

    @staticmethod
    def available(ctx):
        return ctx.host != 'cli' and ctx.task


class Open(Action):
    '''Open a file'''

    label = 'Open'
    identifier = 'file.open'
    parameters = dict(
        file={
            'label': 'File path',
            'required': True,
            'type': types.String,
            'help': 'Path to file you want to publish'
        }
    )

    @staticmethod
    def available(ctx):
        return ctx.host != 'cli' and ctx.task
