# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import shutil
from fstrings import f
from construct.action import Action
from construct.tasks import (
    task,
    requires,
    success,
    pass_context,
    pass_kwargs,
    params,
    store,
    artifact,
    returns,
)
from construct import types
import fsfs


class NewTask(Action):

    label = 'New Task'
    identifier = 'new.task'
    description = 'Create a new Construct Task'

    @staticmethod
    def parameters(ctx):
        params = dict(
            parent={
                'label': 'Parent Entry',
                'required': True,
                'type': fsfs.Entry,
                'help': 'Parent entry of task',
            },
            type={
                'label': 'Task Type',
                'required': True,
                'type': str,
                'help': 'Type of task',
            },
            name={
                'label': 'Task Name',
                'required': False,
                'type': str,
                'help': 'Name of task'
            },
            template={
                'label': 'Task Template Name',
                'required': False,
                'type': str,
                'help': 'Name of task template'
            }
        )

        if not ctx:
            return params

        if ctx.project:
            task_types = ctx.project.read('task_types')
            params['type']['options'] = task_types

        if ctx.shot:
            params['parent']['default'] = ctx.shot
            params['parent']['required'] = False

        elif ctx.asset:
            params['parent']['default'] = ctx.asset
            params['parent']['required'] = False

        return params

    @staticmethod
    def available(ctx):
        return (
            ctx.project
            and (ctx.shot or ctx.asset)
            and not ctx.task
        )


@task(priority=types.STAGE)
@pass_context
@pass_kwargs
@returns(store('task_item'))
def stage_task(ctx, parent, type, name=None, template=None):

    name = name or type
    construct = ctx.construct

    if template:
        template = construct.get_template('task', name=template)

    return dict(
        name=name,
        path=os.path.join(parent.path, name),
        tags=['task', type],
        template=template,
    )


@task(priority=types.VALIDATE)
@requires(success('stage_task'))
@params(store('task_item'))
def validate_task(task_item):
    if os.path.exists(task_item['path']):
        raise OSError('Task already exists: ' + task_item['name'])
    return True


@task(priority=types.COMMIT)
@requires(success('validate_task'))
@params(store('task_item'))
@returns(artifact('task'))
def commit_task(task_item):
    '''Make new task'''

    if task_item['template']:
        task = task_item['template'].copy(task_item['path'])
    else:
        task = fsfs.get_entry(task_item['path'])

    task.tag(*task_item['tags'])

    return task
