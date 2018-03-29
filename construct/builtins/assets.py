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
from construct.errors import Abort
from construct import types
import fsfs


class NewAsset(Action):

    label = 'New Asset'
    identifier = 'new.asset'
    description = 'Create a new Construct Asset'

    @staticmethod
    def parameters(ctx):
        params = dict(
            project={
                'label': 'Project',
                'help': 'Project Entry',
                'required': True,
                'type': types.Entry,
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

        templates = list(api.get_templates('asset').keys())
        if templates:
            params['template']['options'] = templates
            params['template']['default'] = templates[0]

        params['asset_type']['options'] = config['ASSET_TYPES']
        return params

    @staticmethod
    def available(ctx):
        return (
            ctx.project
            and not ctx.sequence
            and not ctx.shot
            and not ctx.asset
        )


@task(priority=types.STAGE)
@pass_kwargs
@returns(store('asset_item'))
def stage_asset(project, asset_type, name, template=None):

    path_template = api.get_path_template('asset')
    asset_path = path_template.format(dict(
        project=project.path,
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
    if os.path.exists(asset_item['path']):
        raise Abort('Asset already exists: ' + asset_item['name'])
    return True


@task(priority=types.COMMIT)
@requires(success('validate_asset'))
@params(store('asset_item'))
@returns(artifact('asset'))
def commit_asset(asset_item):
    '''Make new task'''

    if asset_item['template']:
        asset = asset_item['template'].copy(asset_item['path'])
    else:
        asset = fsfs.get_entry(asset_item['path'])

    asset.tag(*asset_item['tags'])

    return asset
