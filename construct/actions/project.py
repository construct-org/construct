# -*- coding: utf-8 -*-
from __future__ import absolute_import
import fsfs
from construct.core.action import Action
from construct.core.actionrouter import action_router


class NewProject(Action):

    label = 'New Project'
    identifier = 'new.project'
    parameters = dict(
        root={
            'label': 'Project Root',
            'required': True,
            'type': str,
            'help': 'project root directory',
        },
    )
    description = 'Create a new Construct project'

    @staticmethod
    def is_available(context):
        return context.project is None


def tag_project(root):
    fsfs.tag(root, 'project')
    entry = fsfs.Entry(root)
    return entry


tag_project_step = action_router(
    tag_project,
    extractor=lambda a: dict(root=a.kwargs['root']),
    injector=lambda a, r: a.artifacts.update({r.name: r}),
)
