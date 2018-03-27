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
from construct.types import STAGE, COMMIT, VALIDATE
from construct.utils import unipath
import fsfs


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
@pass_context
@pass_kwargs
def stage_template(ctx, **kwargs):
    '''Stage template data'''

    name = kwargs['name']
    entry = kwargs['entry']
    if isinstance(entry, basestring):
        if not os.path.exists(entry):
            raise ActionError('Entry path does not exist: ' + entry)
        entry = fsfs.get_entry(entry)

    templates_path = unipath(ctx.project.data.path, 'templates')
    template_path = unipath(templates_path, name)

    ctx.store.entry = entry
    ctx.store.template_path = template_path


@task(priority=VALIDATE)
@requires(success('stage_template_data'))
@params(kwarg('name'), store('template_path'))
def validate_template(name, template_path):
    '''Make sure template does not already exist'''

    if os.path.exists(template_path):
        raise ActionError('Template already exists: ' + name)


@task(priority=COMMIT)
@requires(success('validate_template'))
@params(store('entry'), store('template_path'), kwarg('include_files'))
@returns(artifact('template'))
def commit_template(entry, template_path, include_files):
    '''Commit template'''

    new_template = entry.copy(template_path, only_data=not include_files)
    return new_template
