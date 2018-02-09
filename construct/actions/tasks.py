# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import shutil
from fstrings import f
from construct.action import Action
from construct.tasks import task, extract, inject, requires, task_success
from construct.context import context
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
@extract(lambda ctx: ctx.kwargs)
@inject(lambda ctx, result: setattr(ctx.store, 'task_item', result))
def stage_task(parent, type, name=None, template=None):

    name = name or type
    construct = context.construct
    if template:
        template = construct.get_template('task', name=template)

    return dict(
        name=name,
        path=os.path.join(parent.path, name),
        tags=['task', type],
        template=template,
    )


@task(priority=types.VALIDATE)
@requires(task_success('stage_task'))
@extract(lambda ctx: (ctx.store.task_item,))
def validate_task(task_item):
    if os.path.exists(task_item['path']):
        raise OSError('Task already exists: ' + task_item['name'])
    return True


@task(priority=types.COMMIT)
@requires(task_success('validate_task'))
@extract(lambda ctx: (ctx.store.task_item,))
@inject(lambda ctx, result: setattr(ctx.artifacts, 'task', result))
def commit_task(task_item):
    '''Make new task'''

    if task_item['template']:
        task = task_item['template'].copy(task_item['path'])
    else:
        task = fsfs.get_entry(task_item['path'])

    task.tag(*task_item['tags'])

    return task
