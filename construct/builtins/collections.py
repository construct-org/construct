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
from construct.errors import Abort
from construct import types
import fsfs


class NewCollection(Action):
    '''Create a new Collection'''

    label = 'New Collection'
    identifier = 'new.collection'
    returns = artifact('collection')

    @staticmethod
    def parameters(ctx):
        params = dict(
            project={
                'label': 'Project',
                'help': 'Project Entry',
                'required': True,
                'type': types.Entry,
            },
            name={
                'label': 'Collection Name',
                'required': True,
                'type': types.String,
                'help': 'Name of Collection',
            },
            template={
                'label': 'Collection Template',
                'require': False,
                'type': types.String,
                'help': 'Name of template',
            },
        )

        if not ctx:
            return params

        if ctx.project:
            params['project']['default'] = ctx.project
            params['project']['required'] = False

        templates = list(api.get_templates('collection').keys())
        if templates:
            params['template']['options'] = templates
            params['template']['default'] = templates[0]

        return params

    @staticmethod
    def available(ctx):
        return (
            ctx.project and
            not ctx.collection
        )


@task(priority=types.STAGE)
@pass_kwargs
@returns(store('collection_item'))
def stage_collection(project, name, template=None):
    '''Stage a new collection'''

    path_template = api.get_path_template('collection')
    collection_path = path_template.format(dict(
        project=project.path,
        collection=name
    ))

    try:
        template = api.get_template(template, 'collection')
    except KeyError:
        template = None

    return dict(
        name=name,
        path=collection_path,
        tags=['collection'],
        template=template,
    )


@task(priority=types.VALIDATE)
@requires(success('stage_collection'))
@params(store('collection_item'))
def validate_collection(collection_item):
    '''Make sure new collection does not exist'''

    if os.path.exists(collection_item['path']):
        raise Abort('collection already exists: ' + collection_item['name'])

    return True


@task(priority=types.COMMIT)
@requires(success('validate_collection'))
@params(store('collection_item'))
@returns(artifact('collection'))
def commit_collection(collection_item):
    '''Make new collection'''

    if collection_item['template']:
        collection = collection_item['template'].copy(collection_item['path'])
    else:
        collection = fsfs.get_entry(collection_item['path'])

    collection.tag(*collection_item['tags'])

    return collection
