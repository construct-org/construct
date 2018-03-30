# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import fsfs
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
        if ctx.host == 'cli':
            return ctx.task
        return True


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
        if ctx.host == 'cli':
            return ctx.task
        return True


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
        if ctx.host == 'cli':
            return ctx.task
        return True


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
        if ctx.host == 'cli':
            # TODO: Create a get_files utility using scandir I reckon
            #       Should support glob patterns or ext as parameter
            import os
            from os.path import join, isfile
            r = os.getcwd()
            files = [p for p in os.listdir(r) if isfile(join(r, p))]
            return files and ctx.project
        return ctx.project
