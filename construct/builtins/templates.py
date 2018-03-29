# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import os
from construct.action import Action
from construct.errors import ActionError
from construct.tasks import (
    task,
    pass_kwargs,
    requires,
    success,
    pass_context,
    store,
    kwarg,
    artifact,
    params,
    returns
)
from construct import types
from construct.utils import unipath
import fsfs


class NewTemplate(Action):

    label = 'New Template'
    identifier = 'new.template'
    description = 'Create a new template from an Entry'

    @staticmethod
    def parameters(ctx):
        params = dict(
            name={
                'label': 'Template Name',
                'required': True,
                'type': types.String,
                'help': 'Name of new template',
            },
            entry={
                'label': 'Entry',
                'required': True,
                'type': types.Entry,
                'help': 'Entry to create template from',
            },
            include_files={
                'label': 'Include Files',
                'type': bool,
                'default': False,
                'help': 'Include all files in entry not just entry data',
            }
        )
        if not ctx:
            return params

        if ctx.host == 'cli':
            params['entry']['default'] = ctx.get_deepest_entry()

        return params

    @staticmethod
    def available(ctx):
        return any([
            not ctx.project,
            ctx.shot,
            ctx.asset,
            ctx.task,
            ctx.workspace
        ])


@task(priority=types.STAGE)
@pass_kwargs
def stage_template(**kwargs):
    '''Stage template data'''

    name = kwargs['name']
    entry = kwargs['entry']

    templates_path = unipath(ctx.project.data.path, 'templates')
    template_path = unipath(templates_path, name)

    ctx.store.entry = entry
    ctx.store.template_path = template_path


@task(priority=types.VALIDATE)
@requires(success('stage_template_data'))
@params(kwarg('name'), store('template_path'))
def validate_template(name, template_path):
    '''Make sure template does not already exist'''

    if os.path.exists(template_path):
        raise Abort('Template already exists: ' + name)


@task(priority=types.COMMIT)
@requires(success('validate_template'))
@params(store('entry'), store('template_path'), kwarg('include_files'))
@returns(artifact('template'))
def commit_template(entry, template_path, include_files):
    '''Commit template'''

    new_template = entry.copy(template_path, only_data=not include_files)
    return new_template
