# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import shutil
from construct.action import Action
from construct.tasks import (
    task,
    pass_kwargs,
    pass_context,
    returns,
    artifact,
    store,
    params,
    success,
    requires,
)
from construct.errors import Abort
from construct import types, get_host, utils, get_path_template, get_file_type
from construct.vendor.lucidity.error import ParseError


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
                'help': 'Workspace to save to',
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
                'help': 'File Version',
            },
            ext={
                'label': 'Extension',
                'require': True,
                'type': types.String,
                'help': 'File Extension',
            },
        )

        if not ctx:
            return params

        params['workspace']['default'] = ctx.workspace
        name = ctx.task.parent().name
        extensions = ctx.workspace.config['extensions']
        extension = extensions[0]
        path_template = get_path_template('workspace_file')
        try:
            data = path_template.parse(str(ctx.file))
        except ParseError:
            pass
        else:
            name = data['name']
            extension = data['ext']

        params['name']['default'] = name

        params['ext']['default'] = extension
        params['ext']['options'] = extensions
        params['ext']['required'] = False

        next_version = ctx.workspace.get_next_version(name, extension)
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
        extensions = ctx.workspace.config['extensions']
        extension = extensions[0]
        path_template = get_path_template('workspace_file')
        try:
            data = path_template.parse(str(ctx.file))
        except ParseError:
            pass
        else:
            name = data['name']
            extension = data['ext']

        params['name']['default'] = name

        params['ext']['default'] = extension
        params['ext']['options'] = extensions
        params['ext']['required'] = False

        next_version = ctx.workspace.get_next_version(name, extension)
        params['version']['default'] = next_version
        params['version']['required'] = False

        return params

    @staticmethod
    def available(ctx):
        return ctx.host != 'cli' and ctx.workspace and ctx.file


class Publish(Action):
    '''Publish the current open file'''

    label = 'Publish'
    identifier = 'publish'
    returns = artifact('file')

    @staticmethod
    def parameters(ctx):
        return {}

    @staticmethod
    def available(ctx):
        return ctx.host != 'cli' and ctx.task and ctx.file


@task(priority=types.STAGE)
@pass_context
@returns(store('publish_items'))
def stage_scene(ctx):
    '''Stage the current work file as a publish item'''

    path_template = get_path_template('workspace_file')
    scene_data = path_template.parse(str(ctx.file))
    file_type = get_file_type(str(ctx.file))
    if file_type:
        file_type = file_type[0]
    else:
        file_type = scene_data['ext'][1:]
    publish_path = get_path_template('publish').format(dict(
        task=str(ctx.task),
        file_type=file_type,
    ))
    publish_file = get_path_template('publish_file').format(scene_data)
    publish_item = dict(
        type='scene',
        task=ctx.task,
        scene_data=scene_data,
        scene_root=os.path.dirname(str(ctx.file)),
        scene_file=str(ctx.file),
        publish_root=publish_path,
        publish_file=utils.unipath(publish_path, publish_file),
    )
    return {'scene': publish_item}


@task(priority=types.VALIDATE)
@params(store('publish_items'))
@requires(success('stage_scene'))
def validate_scene(publish_items):
    '''Validate the scene file.'''

    # Ensure publish scene does not exist
    scene = publish_items['scene']
    if os.path.isfile(scene['publish_file']):
        raise Abort(
            'Publish file already exists: %s' %
            os.path.basename(scene['publish_file'])
        )


@task(priority=types.VALIDATE)
@params(store('publish_items'))
@requires(success('validate_scene'))
def ensure_saved(publish_items):
    '''Make sure workfile is saved before publishing.'''

    scene = publish_items['scene']
    host = get_host()
    host.save_file(scene['scene_file'])


@task(priority=types.COMMIT)
@pass_context
@params(store('publish_items'))
@requires(success('validate_scene'))
def publish_scene(ctx, publish_items):
    '''Publish the current scene file.'''

    scene = publish_items['scene']
    host = get_host()
    host.save_file(scene['publish_file'])


@task(priority=types.COMMIT)
@pass_context
@params(store('publish_items'))
@requires(success('publish_scene'))
@returns(store('next_scene_file'))
def save_next_workfile(ctx, publish_items):
    '''Save the next workfile.'''

    host = get_host()
    scene = publish_items['scene']

    # Get the next version number for the original scene name
    if ctx.workspace:
        next_version = ctx.workspace.get_next_version(
            scene['scene_data']['name'],
            scene['scene_data']['ext'],
        )
    else:
        next_version = int(scene['scene_data']['version']) + 1

    # Construct the next scene_file path
    next_scene_name = scene['scene_file'].replace(
        scene['scene_data']['version'],
        '{:0>3d}'.format(next_version),
    )
    next_scene_file = utils.unipath(scene['scene_root'], next_scene_name)

    # If the path already exists Abort...
    if os.path.isfile(next_scene_file):
        raise Abort('Next scene file already exists. Reopening workfile.')

    # Copy the original scene file to the next version
    shutil.copy2(scene['scene_file'], next_scene_file)

    return next_scene_file


@task(priority=types.COMMIT)
@params(store('next_scene_file'))
@requires(success('save_next_workfile'))
def open_next_workfile(next_scene_file):
    '''Open the next workfile.'''

    host = get_host()
    host.open_file(next_scene_file)
