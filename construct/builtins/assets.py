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


class NewAssetType(Action):
    '''Create a new Asset Type'''

    label = 'New Asset Type'
    identifier = 'new.asset_type'
    returns = artifact('asset_type')

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
                'label': 'Asset Type Name',
                'required': True,
                'type': types.String,
                'help': 'Name of Asset Type',
            },
        )

        if not ctx:
            return params

        if ctx.project:
            params['project']['default'] = ctx.project
            params['project']['required'] = False

        if ctx.collection:
            params['collection']['default'] = ctx.collection.name
            params['collection']['required'] = False

        return params

    @staticmethod
    def available(ctx):
        return (
            ctx.project and
            ctx.collection and
            not ctx.asset_type and
            not ctx.sequence
        )


@task(priority=types.STAGE)
@pass_kwargs
@returns(store('asset_type'))
def stage_asset_type(project, collection, name):
    '''Stage new asset_type Entry'''

    path_template = api.get_path_template('asset_type')
    asset_type_path = path_template.format(dict(
        project=project.path,
        collection=collection,
        asset_type=name,
    ))

    return fsfs.get_entry(asset_type_path)


@task(priority=types.VALIDATE)
@requires(success('stage_asset_type'))
@params(store('asset_type'))
def validate_asset_type(asset_type):
    '''Make sure new asset_type does not already exist'''

    if asset_type.exists:
        raise Abort('Asset Type already exists: %s' % asset_type.name)
    return True


@task(priority=types.COMMIT)
@requires(success('validate_asset_type'))
@params(store('asset_type'))
@returns(artifact('asset_type'))
def commit_asset_type(asset_type):
    '''Commit new asset_type Entry'''

    asset_type.tag('asset_type')
    return asset_type


class NewAsset(Action):
    '''Create a new Asset'''

    label = 'New Asset'
    identifier = 'new.asset'
    returns = artifact('asset')

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
            asset_type={
                'label': 'Asset Type',
                'required': True,
                'type': types.String,
                'help': 'Type of asset',
            },
            name={
                'label': 'Asset Name',
                'required': True,
                'type': types.String,
                'help': 'Name of asset'
            },
            template={
                'label': 'Asset Template',
                'required': False,
                'type': types.String,
                'help': 'Name of asset template'
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

            # asset_types = [e.name for e in ctx.project.asset_types]
            # params['asset_type']['options'] = asset_types

        if ctx.collection:
            params['collection']['default'] = ctx.collection.name
            params['collection']['required'] = False

        if ctx.asset_type:
            params['asset_type']['default'] = ctx.asset_type.name
            params['asset_type']['required'] = False

        templates = list(api.get_templates('asset').keys())
        if templates:
            params['template']['options'] = templates
            params['template']['default'] = sorted(templates)[0]

        return params

    @staticmethod
    def available(ctx):
        return (
            ctx.project and
            ctx.collection and
            ctx.asset_type and
            not ctx.asset
        )


@task(priority=types.STAGE)
@pass_kwargs
@returns(store('asset_item'))
def stage_asset(project, collection, asset_type, name, template=None):
    '''Stage a new Asset'''

    path_template = api.get_path_template('asset')
    asset_path = path_template.format(dict(
        project=project.path,
        collection=collection,
        asset_type=asset_type,
        asset=name
    ))

    try:
        template = api.get_template(template, 'asset')
    except KeyError:
        template = None

    return dict(
        name=name,
        path=asset_path,
        tags=['asset'],
        template=template,
    )


@task(priority=types.VALIDATE)
@requires(success('stage_asset'))
@params(store('asset_item'))
def validate_asset(asset_item):
    '''Make sure new asset does not exist'''

    if os.path.exists(asset_item['path']):
        raise Abort('Asset already exists: ' + asset_item['name'])
    return True


@task(priority=types.COMMIT)
@requires(success('validate_asset'))
@params(store('asset_item'))
@returns(artifact('asset'))
def commit_asset(asset_item):
    '''Make new asset'''

    if asset_item['template']:
        asset = asset_item['template'].copy(asset_item['path'])
    else:
        asset = fsfs.get_entry(asset_item['path'])

    asset.tag(*asset_item['tags'])

    return asset
