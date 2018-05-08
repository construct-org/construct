# -*- coding: utf-8 -*-
from __future__ import absolute_import
from construct.action import Action
from construct.tasks import (
    task,
    pass_kwargs,
    returns,
    artifact,
    store,
    params,
    success,
    requires
)
from construct import types, get_host


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
            },
            extension={
                'label': 'Extension',
                'require': True,
                'type': types.String,
                'help': 'File Extension'
            }
        )

        if not ctx:
            return params

        params['workspace']['default'] = ctx.workspace
        params['name']['default'] = ctx.task.parent().name
        params['version']['default'] = 1

        extensions = ctx.workspace.config['extensions']
        params['extension']['default'] = extensions[0]
        params['extension']['options'] = extensions
        params['extension']['required'] = False
        return params

    @staticmethod
    def available(ctx):
        return ctx.host != 'cli' and ctx.workspace

@task
@pass_kwargs
@returns(store('file'))
def build_filename(workspace, name, version, extension):
    '''Builds the full save path'''
    pass


@task
@requires(success('build_filepath'))
@params(store('file'))
def save_file(file):
    '''Save file in Host application'''

    host = get_host()
    host.save_file(file)


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


@task
@pass_kwargs
def open_file(file):
    '''Open file in Host application'''

    host = get_host()
    host.open_file(file)
