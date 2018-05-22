# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import construct
from construct.action import Action
from construct.errors import Abort
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


class NewTemplate(Action):
    '''Create a new Template from an Entry'''

    label = 'New Template'
    identifier = 'new.template'
    returns = artifact('template')

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
        return False


@task(priority=types.STAGE)
@pass_context
@pass_kwargs
@returns(store('template'))
def stage_template(ctx, name, entry, include_files):
    '''Stage template data'''

    templates_path = unipath(ctx.project.data.path, 'templates')
    template_path = unipath(templates_path, name)

    template_item = types.Namespace(
        entry=entry,
        name=name,
        path=template_path,
        include_files=include_files,
    )
    return template_item


@task(priority=types.VALIDATE)
@requires(success('stage_template_data'))
@params(store('template'))
def validate_template(template):
    '''Make sure template does not already exist'''

    if (
        os.path.exists(template.path) or
        template.name in construct.get_templates()
    ):
        raise Abort('Template already exists: ' + template.name)


@task(priority=types.COMMIT)
@requires(success('validate_template'))
@params(store('template'))
@returns(artifact('template'))
def commit_template(template):
    '''Commit template'''

    new_template = entry.copy(template_path, only_data=not include_files)
    return new_template
