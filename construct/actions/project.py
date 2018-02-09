# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import shutil
from construct.action import Action
from construct.tasks import task, extract, inject, requires
import fsfs
from construct.context import context


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
            'required': False,
            'type': str,
            'help': 'name of a project template',
        }
    )

    @classmethod
    def parameters(cls, ctx):
        params = dict(cls._parameters)

        if ctx and 'construct' in ctx:
            templates = ctx.construct.get_template('project')
            if templates:
                params['template']['options'] = [t.name for t in templates]

        return params

    @staticmethod
    def available(ctx):
        return not ctx.project


# TODO: allow users to create projects using configs stored in a git repo
# TODO: allow users to create projects using configs stored in any folder


@task
@extract(lambda ctx: ctx.kwargs)
@inject(lambda ctx, result: setattr(ctx.artifacts, 'project', result))
def make_new_project(root, template):
    '''Make a new project'''

    construct = context.construct
    if os.path.exists(root):
        raise OSError('Root already exists: ' + root)

    template = construct.get_template('project', name=template)
    project = template.copy(root)

    return project
