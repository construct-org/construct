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


class NewSequence(Action):
    '''Create a new Sequence'''

    label = 'New Sequence'
    identifier = 'new.sequence'
    returns = artifact('sequence')

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
            name={
                'label': 'Sequence Name',
                'required': True,
                'type': types.String,
                'help': 'Name of sequence',
            },
            template={
                'label': 'Sequence Template',
                'required': False,
                'type': types.String,
                'help': 'Name of sequence template'
            }
        )

        if not ctx:
            return params

        if ctx.project:
            params['project']['default'] = ctx.project
            params['project']['required'] = False

            # TODO: fix search speed upstream...
            # collection_types = [e.name for e in ctx.project.collections]
            # params['collection']['options'] = collection_types

        if ctx.collection:
            params['collection']['default'] = ctx.collection.name
            params['collection']['required'] = False

        templates = list(api.get_templates('sequence').keys())
        if templates:
            params['template']['default'] = templates[0]
            params['template']['options'] = templates

        return params

    @staticmethod
    def available(ctx):
        return (
            ctx.project and
            ctx.collection and
            not ctx.sequence and
            not ctx.asset_type
        )


@task(priority=types.STAGE)
@pass_kwargs
@returns(store('sequence_item'))
def stage_sequence(project, collection, name, template=None):

    path_template = api.get_path_template('sequence')
    sequence_path = path_template.format(dict(
        project=project.path,
        collection=collection,
        sequence=name
    ))

    try:
        template = api.get_template(template, 'sequence')
    except KeyError:
        template = None

    return dict(
        name=name,
        path=sequence_path,
        tags=['sequence'],
        template=template,
    )


@task(priority=types.VALIDATE)
@requires(success('stage_sequence'))
@params(store('sequence_item'))
def validate_sequence(sequence_item):
    if os.path.exists(sequence_item['path']):
        raise Abort('Sequence already exists: ' + sequence_item['name'])
    return True


@task(priority=types.COMMIT)
@requires(success('validate_sequence'))
@params(store('sequence_item'))
@returns(artifact('sequence'))
def commit_sequence(sequence_item):
    '''Make new task'''

    if sequence_item['template']:
        sequence = sequence_item['template'].copy(sequence_item['path'])
    else:
        sequence = fsfs.get_entry(sequence_item['path'])

    sequence.tag(*sequence_item['tags'])

    return sequence
