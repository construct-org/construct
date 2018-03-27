# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import shutil
import construct
from construct.action import Action
from construct.tasks import task, pass_context, pass_kwargs, returns, artifact
from construct.errors import Abort
import fsfs


class NewProject(Action):

    label = 'New Project'
    identifier = 'new.project'
    description = 'Create a new Construct project'
    _parameters = dict(
        root={
            'label': 'Project Root',
            'required': True,
            'type': str,
            'help': 'project root directory',
        },
        template={
            'label': 'Project Template',
            'required': True,
            'type': str,
            'help': 'name of a project template',
        }
    )

    @classmethod
    def parameters(cls, ctx):
        params = dict(cls._parameters)

        if ctx:
            templates = construct.get_templates('project')
            if templates:
                opt = params['template']
                opt['options'] = [str(t.name) for t in templates.values()]
                opt['default'] = opt['options'][0]

        return params

    @staticmethod
    def available(ctx):
        return not ctx.project


@task
@pass_context
@pass_kwargs
@returns(artifact('project'))
def make_new_project(ctx, root, template):
    '''Make a new project'''

    if os.path.exists(root):
        raise Abort('Root already exists: ' + root)

    template = construct.get_template(template)
    project = template.copy(root)

    return project
