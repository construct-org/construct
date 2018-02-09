# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import os
import shutil
from construct.action import Action
from construct.err import ActionError
from construct.tasks import task, extract, requires, task_success
from construct.types import STAGE, COMMIT, VALIDATE
from construct.util import unipath
import fsfs
from construct.context import context


class NewTemplate(Action):

    label = 'New Template'
    identifier = 'new.template'
    description = 'Create a new template from an Entry'
    _parameters = dict(
        name={
            'label': 'Template Name',
            'required': True,
            'type': str,
            'help': 'Name of new template',
        },
        entry={
            'label': 'Entry',
            'required': False,
            'type': (fsfs.Entry, str),
            'help': 'Entry path',
        },
        include_files={
            'label': 'Include Files',
            'required': True,
            'type': bool,
            'default': False,
            'help': 'Include all files in entry not just entry data',
        }
    )

    @classmethod
    def parameters(cls, ctx):
        params = dict(cls._parameters)
        if ctx and ctx.host == 'cli':
            params['entry']['default'] = ctx.get_deepest_entry()
        return params

    @staticmethod
    def available(ctx):
        if ctx.host == 'cli':
            return (
                ctx.project
                and any([
                    ctx.sequence, ctx.shot, ctx.asset, ctx.task, ctx.workspace
                ])
            )
        return ctx.project


@task(priority=STAGE)
def stage_template_data():
    '''Stage template data'''

    name = context.kwargs['name']
    entry = context.kwargs['entry']
    if isinstance(entry, basestring):
        if not os.path.exists(entry):
            raise ActionError('Entry path does not exist: ' + entry)
        entry = fsfs.get_entry(entry)

    templates_path = unipath(context.project.data.path, 'templates')
    template_path = unipath(templates_path, name)

    context.store.entry = entry
    context.store.template_path = template_path


@task(priority=VALIDATE)
@requires(task_success('stage_template_data'))
def validate_template():
    '''Make sure template does not already exist'''

    if os.path.exists(context.store.template_path):
        raise ActionError('Template already exists: ' + context.kwargs['name'])


@task(priority=COMMIT)
@requires(task_success('validate_template'))
def commit_template():
    '''Commit template'''

    entry = context.store.entry
    template_path = context.store.template_path
    only_data = not context.kwargs['include_files']
    new_template = entry.copy(template_path, only_data=only_data)
    context.artifacts.template = new_template
