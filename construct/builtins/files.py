# -*- coding: utf-8 -*-
from __future__ import absolute_import
from construct.action import Action
from construct.tasks import artifact
from construct import types


class Publish(Action):
    '''Publish the current open file'''

    label = 'Publish'
    identifier = 'publish'
    returns = artifact('file')

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
    returns = artifact('file')

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
    returns = artifact('file')

    @staticmethod
    def parameters(ctx):
        params = dict(
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

        if not ctx:
            return params

        params['workspace']['default'] = ctx.workspace
        params['name']['default'] = ctx.task.parent().name
        params['version']['default'] = 1
        return params

    @staticmethod
    def available(ctx):
        return ctx.host != 'cli' and ctx.workspace


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
