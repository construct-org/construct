# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
from construct import api, config
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
from construct import types
from construct.errors import Abort
import fsfs


class NewProject(Action):

    label = 'New Project'
    identifier = 'new.project'
    description = 'Create a new Project'

    @classmethod
    def parameters(cls, ctx):
        params = dict(
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

        if not ctx:
            return params

        templates = list(api.get_templates('project').keys())
        params['template']['options'] = templates
        if templates:
            params['template']['default'] = templates[0]

        return params

    @staticmethod
    def available(ctx):
        return not ctx.project


@task(priority=types.STAGE)
@pass_kwargs
@returns(store('project_item'))
def stage_project(root, template):
    '''Stage project data for validation'''

    return dict(
        path=unipath(root),
        name=os.path.basename(root),
        template=api.get_template(template)
    )


@task(priority=types.VALIDATE)
@params(store('project_item'))
@requires(success('stage_project'))
def validate_project(project_item):
    '''Make sure the project does not already exist.'''

    if os.path.exists(project_item['path']):
        raise Abort('Project already exists: %s' % project_item['path'])

    return True


@task(priority=types.COMMIT)
@params(store('project_item'))
@requires(success('validate_project'))
@returns(artifact('project'))
def commit_project(project_item):
    '''Copy the project template to project directory'''

    project = project_item['template'].copy(project_item['path'])
    return project
