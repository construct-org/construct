# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
from construct import api
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


class NewShot(Action):
    '''Create a new Shot'''

    label = 'New Shot'
    identifier = 'new.shot'
    returns = artifact('shot')

    @staticmethod
    def parameters(ctx):
        params = dict(
            project={
                'label': 'Project',
                'help': 'Project Entry',
                'required': True,
                'type': types.Entry,
            },
            collection={
                'label': 'Collection',
                'help': 'Collection Name',
                'required': True,
                'type': types.String
            },
            sequence={
                'label': 'Sequence',
                'required': True,
                'type': types.Entry,
                'help': 'Name of sequence',
            },
            name={
                'label': 'Shot Name',
                'required': True,
                'type': types.String,
                'help': 'Name of shot'
            },
            template={
                'label': 'Shot Template',
                'required': False,
                'type': types.String,
                'help': 'Name of shot template'
            }
        )

        if not ctx:
            return params

        if ctx.project:
            params['project']['default'] = ctx.project
            params['project']['required'] = False

            collection_types = [e.name for e in ctx.project.collections]
            params['collection']['options'] = collection_types

        if ctx.collection:
            params['collection']['default'] = ctx.collection.name
            params['collection']['required'] = False

        if ctx.sequence:
            params['sequence']['default'] = ctx.sequence
            params['sequence']['required'] = False

        templates = list(api.get_templates('shot').keys())
        if templates:
            params['template']['options'] = templates
            params['template']['default'] = sorted(templates)[0]

        return params

    @staticmethod
    def available(ctx):
        return (
            ctx.project and
            ctx.collection and
            ctx.sequence and
            not ctx.shot
        )


@task(priority=types.STAGE)
@pass_kwargs
@returns(store('shot_item'))
def stage_shot(project, collection, sequence, name, template=None):

    path_template = api.get_path_template('shot')
    shot_path = path_template.format(dict(
        project=project.path,
        collection=collection,
        sequence=sequence.name,
        shot=name
    ))

    try:
        template = api.get_template(template, 'shot')
    except KeyError:
        template = None

    return dict(
        name=name,
        path=shot_path,
        tags=['shot'],
        template=template,
    )


@task(priority=types.VALIDATE)
@requires(success('stage_shot'))
@params(store('shot_item'))
def validate_shot(shot_item):
    if os.path.exists(shot_item['path']):
        raise Abort('Shot already exists: ' + shot_item['name'])
    return True


@task(priority=types.COMMIT)
@requires(success('validate_shot'))
@params(store('shot_item'))
@returns(artifact('shot'))
def commit_shot(shot_item):
    '''Make new task'''

    if shot_item['template']:
        shot = shot_item['template'].copy(shot_item['path'])
    else:
        shot = fsfs.get_entry(shot_item['path'])

    shot.tag(*shot_item['tags'])

    return shot
