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
from construct import types, get_host, utils, get_path_template
from construct.vendor.lucidity.error import ParseError


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
            ext={
                'label': 'Extension',
                'require': True,
                'type': types.String,
                'help': 'File Extension'
            }
        )

        if not ctx:
            return params

        params['workspace']['default'] = ctx.workspace
        name = ctx.task.parent().name
        if ctx.file:
            path_template = get_path_template('workspace_file')
            try:
                data = path_template.parse(str(ctx.file))
            except ParseError:
                pass
            else:
                name = data['name']

        params['name']['default'] = name

        extensions = ctx.workspace.config['extensions']
        params['ext']['default'] = extensions[0]
        params['ext']['options'] = extensions
        params['ext']['required'] = False
        next_version = ctx.workspace.get_next_version(name, extensions[0])
        params['version']['default'] = next_version
        params['version']['required'] = False
        return params

    @staticmethod
    def available(ctx):
        return ctx.host != 'cli' and ctx.workspace


@task
@pass_kwargs
@returns(store('file'))
def build_filename(workspace, name, version, ext):
    '''Builds the full save path'''

    task = workspace.parent()
    path_template = get_path_template('workspace_file')
    filename = path_template.format(dict(
        task=task.short,
        name=name,
        version='{:0>3d}'.format(version),
        ext=ext
    ))
    return utils.unipath(workspace.path, filename)


@task
@requires(success('build_filename'))
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


class SaveNextVersion(Action):
    '''Save the current file'''

    label = 'Save Next Version'
    identifier = 'file.save_next'
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
                'required': True,
                'type': types.String,
                'help': 'Filename',
            },
            version={
                'label': 'Version',
                'required': True,
                'type': types.Integer,
                'help': 'File Version'
            },
            ext={
                'label': 'Extension',
                'require': True,
                'type': types.String,
                'help': 'File Extension'
            }
        )

        if not ctx:
            return params

        params['workspace']['default'] = ctx.workspace
        name = ctx.task.parent().name
        path_template = get_path_template('workspace_file')
        try:
            data = path_template.parse(str(ctx.file))
        except ParseError:
            pass
        else:
            name = data['name']

        params['name']['default'] = name

        extensions = ctx.workspace.config['extensions']
        params['ext']['default'] = extensions[0]
        params['ext']['options'] = extensions
        params['ext']['required'] = False

        next_version = ctx.workspace.get_next_version(name, extensions[0])
        params['version']['default'] = next_version
        params['version']['required'] = False

        return params

    @staticmethod
    def available(ctx):
        return ctx.host != 'cli' and ctx.workspace and ctx.file
