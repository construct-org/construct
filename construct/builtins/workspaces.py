# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
from construct.action import Action
from construct.tasks import (
    task,
    pass_kwargs,
    requires,
    success,
    pass_context,
    store,
    kwarg,
    artifact,
    returns,
    params
)
from construct import types, api
from construct.errors import Abort, Disable
import fsfs


class NewWorkspace(Action):
    '''Create a new Workspace'''

    label = 'New Workspace'
    identifier = 'new.workspace'
    returns = artifact('workspace')

    @staticmethod
    def parameters(ctx):
        params = dict(
            task={
                'label': 'Parent Entry',
                'required': True,
                'type': types.Entry,
                'help': 'Parent entry of workspace',
            },
            name={
                'label': 'Workspace Name',
                'required': True,
                'type': types.String,
                'help': 'Name of workspace'
            },
            template={
                'label': 'Workspace Template Name',
                'required': True,
                'type': types.String,
                'help': 'Name of workspace template'
            }
        )

        if not ctx:
            return params

        if ctx.task:
            params['task']['default'] = ctx.task
            params['task']['required'] = False

        templates = api.get_templates('workspace')
        if templates:
            params['template']['options'] = list(templates.keys())

        return params

    @staticmethod
    def available(ctx):
        return (
            ctx.project and
            (ctx.shot or ctx.asset) and
            ctx.task and
            not ctx.workspace
        )


@task(priority=types.STAGE)
@pass_kwargs
@returns(store('workspace_item'))
def stage_workspace(task, name=None, template=None):
    '''Stage workspace for creation'''

    path_template = api.get_path_template('workspace')
    path = path_template.format(dict(
        task=task.path,
        workspace=name
    ))
    name = name
    return dict(
        name=name,
        path=path,
        tags=['workspace'],
        template=api.get_template(template, 'workspace'),
    )


@task(priority=types.VALIDATE)
@requires(success('stage_workspace'))
@params(store('workspace_item'))
def validate_workspace(workspace_item):
    '''Validate potential workspace'''

    if os.path.exists(workspace_item['path']):
        raise Abort('Task already exists: ' + workspace_item['name'])
    return True


@task(priority=types.COMMIT)
@requires(success('validate_workspace'))
@params(store('workspace_item'))
@returns(artifact('workspace'))
def commit_workspace(workspace_item):
    '''Create new workspace'''

    if workspace_item['template']:
        workspace = workspace_item['template'].copy(workspace_item['path'])
    else:
        workspace = fsfs.get_entry(workspace_item['path'])

    workspace.tag(*workspace_item['tags'])

    return workspace


class SetWorkspace(Action):
    '''Set the current workspace'''

    label = 'Set Workspace'
    identifier = 'set_workspace'
    returns = artifact('workspace')

    @staticmethod
    def parameters(ctx):
        params = dict(
            task={
                'label': 'Parent Entry',
                'required': True,
                'type': types.Entry,
                'help': 'Parent entry of workspace',
            },
            name={
                'label': 'Workspace Name',
                'required': True,
                'type': types.String,
                'help': 'Name of workspace'
            },
            template={
                'label': 'Workspace template Name',
                'required': True,
                'type': types.String,
                'help': 'Name of template to use if the task has no workspace'
            }
        )

        if not ctx:
            return params

        if ctx.task:
            params['task']['default'] = ctx.task
            params['task']['required'] = False

        # Get default workspace for this host
        host = api.get_host()
        params['name']['default'] = host.name

        default_workspace = host.name
        for name, data in api.config['SOFTWARE'].items():
            if data['host'] == host.name:
                default_workspace = data['default_workspace']
                break

        template = api.get_template(default_workspace, 'workspace')
        if template:
            params['template']['default'] = template.name

        templates = api.get_templates('workspace')
        if templates:
            params['template']['options'] = list(templates.keys())

        return params

    @staticmethod
    def available(ctx):
        return ctx.host != 'cli' and ctx.project


@task(priority=types.COMMIT)
@pass_context
@pass_kwargs
def set_workspace(ctx, task, name, template):
    '''Create new workspace'''

    # If ensure_workspace created a workspace, use it
    if 'workspace' in ctx.artifacts:
        workspace = ctx.artifacts.workspace
    else:
        workspace = task.workspaces.name(name).one()

    host = api.get_host()
    host.set_workspace(workspace.path)
    api.set_context_from_path(workspace.path)


@task(priority=types.VALIDATE)
@pass_context
@pass_kwargs
@returns(artifact('workspace'))
def ensure_workspace(ctx, task, name, template):
    '''Setup a workspace for the current task'''

    workspace = task.workspaces.name(name).one()
    if workspace:
        raise Disable('Workspace already exists.')

    if not template:
        raise Disable('Could not find a workspace for %s' % task)

    path_template = api.get_path_template('workspace')
    template = api.get_template(template, 'workspace')

    path = path_template.format(dict(
        task=task.path,
        workspace=name,
    ))

    if os.path.exists(path):
        import fsfs
        workspace = fsfs.get_entry(path)
        workspace.tag(*template.tags)
        workspace.write(**template.read())
    else:
        workspace = template.copy(path)

    return workspace
