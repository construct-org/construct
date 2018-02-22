# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import shutil
from fstrings import f
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
from construct import types
import fsfs


class NewWorkspace(Action):

    label = 'New Workspace'
    identifier = 'new.workspace'
    description = 'Create a new Construct Workspace'

    @staticmethod
    def parameters(ctx):
        params = dict(
            parent={
                'label': 'Parent Entry',
                'required': True,
                'type': fsfs.Entry,
                'help': 'Parent entry of workspace',
            },
            name={
                'label': 'Workspace Name',
                'required': True,
                'type': str,
                'help': 'Name of workspace'
            },
            template={
                'label': 'Workspace Template Name',
                'required': False,
                'type': str,
                'help': 'Name of workspace template'
            }
        )

        if not ctx:
            return params

        if ctx.task:
            params['parent']['default'] = ctx.task
            params['parent']['required'] = False

        if 'construct' in ctx:
            templates = ctx.construct.get_template('workspace')
            if templates:
                params['template']['options'] = [t.name for t in templates]

        return params

    @staticmethod
    def available(ctx):
        return (
            ctx.project
            and (ctx.shot or ctx.asset)
            and ctx.task
            and not ctx.workspace
        )


@task(priority=types.STAGE)
@pass_context
@pass_kwargs
@returns(store('workspace_item'))
def stage_workspace(ctx, parent, name=None, template=None):
    '''Stage a workspace for creation'''

    name = name or template
    construct = ctx.construct
    if template:
        template = construct.get_template('workspace', name=template)

    path_template = construct.get_path_template('workspace')

    return dict(
        name=name,
        path=path_template.format(parent=parent.path, workspace=name),
        tags=['workspace'],
        template=template,
    )


@task(priority=types.VALIDATE)
@params(store('workspace_item'))
@requires(success('stage_workspace'))
def validate_workspace(workspace_item):
    '''Validate workspace'''

    if os.path.exists(workspace_item['path']):
        raise OSError('Workspace already exists: ' + workspace_item['name'])
    return True


@task(priority=types.COMMIT)
@requires(success('validate_workspace'))
@params(store('workspace_item'))
@returns(artifact('workspace'))
def commit_workspace(workspace_item):
    '''Make new workspace'''

    if workspace_item['template']:
        workspace = workspace_item['template'].copy(workspace_item['path'])
    else:
        workspace = fsfs.get_entry(workspace_item['path'])

    workspace.tag(*workspace_item['tags'])

    return workspace
