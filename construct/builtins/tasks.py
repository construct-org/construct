# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
from construct import api, config, types
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
from construct.utils import unipath
from construct.errors import Abort
import fsfs


class NewTask(Action):
    '''Create a new Task'''

    label = 'New Task'
    identifier = 'new.task'
    returns = artifact('task')

    @staticmethod
    def parameters(ctx):
        params = dict(
            parent={
                'label': 'Parent Entry',
                'required': True,
                'type': types.Entry,
                'help': 'Parent entry of task',
            },
            type={
                'label': 'Task Type',
                'required': True,
                'type': types.String,
                'help': 'Type of task',
            },
            name={
                'label': 'Task Name',
                'required': False,
                'type': types.String,
                'help': 'Name of task'
            },
            template={
                'label': 'Task Template Name',
                'required': False,
                'type': types.String,
                'help': 'Name of task template'
            }
        )

        if not ctx:
            return params

        params['type']['options'] = list(config['TASK_TYPES'].keys())

        if ctx.shot:
            params['parent']['default'] = ctx.shot
            params['parent']['required'] = False

        elif ctx.asset:
            params['parent']['default'] = ctx.asset
            params['parent']['required'] = False

        templates = list(api.get_templates('task').keys())
        if templates:
            params['template']['options'] = templates
            params['template']['default'] = templates[0]

        return params

    @staticmethod
    def available(ctx):
        return (
            ctx.project and
            (ctx.shot or ctx.asset) and
            not ctx.task
        )


@task(priority=types.STAGE)
@pass_kwargs
@returns(store('task_item'))
def stage_task(parent, type, name=None, template=None):
    '''Stage task for creation'''

    name = name or type
    return dict(
        name=name,
        path=unipath(parent.path, name),
        tags=['task', type],
        template=api.get_template(template, 'task'),
    )


@task(priority=types.VALIDATE)
@requires(success('stage_task'))
@params(store('task_item'))
def validate_task(task_item):
    '''Validate potential task'''

    if os.path.exists(task_item['path']):
        raise Abort('Task already exists: ' + task_item['name'])
    return True


@task(priority=types.COMMIT)
@requires(success('validate_task'))
@params(store('task_item'))
@returns(artifact('task'))
def commit_task(task_item):
    '''Create new task'''

    if task_item['template']:
        task = task_item['template'].copy(task_item['path'])
    else:
        task = fsfs.get_entry(task_item['path'])

    task.tag(*task_item['tags'])

    return task
