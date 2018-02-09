# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import shutil
from construct.action import Action
from construct.tasks import task, extract, inject, requires
import fsfs
from construct.context import context


class NewAsset(Action):

    label = 'New Asset'
    identifier = 'new.asset'
    description = 'Create a new Construct Asset'
    _parameters = dict(
        type={
            'label': 'Asset Type',
            'required': True,
            'type': str,
            'help': 'Type of asset',
        },
        name={
            'label': 'Asset Name',
            'required': True,
            'type': str,
            'help': 'Name of asset'
        },
        template={
            'label': 'Asset Template',
            'required': False,
            'type': str,
            'help': 'Name of asset template'
        }
    )

    @classmethod
    def parameters(cls, ctx):
        params = dict(cls._parameters)

        if ctx and ctx.project:
            templates = ctx.construct.get_template('asset')
            if templates:
                params['template']['options'] = [t.name for t in templates]

            asset_types = ctx.project.read().get('asset_types', None)
            if asset_types:
                params['type']['options'] = asset_types

        return params

    @staticmethod
    def available(ctx):
        return (
            ctx.project
            and not ctx.sequence
            and not ctx.shot
            and not ctx.asset
        )


@task
@extract(lambda ctx: ctx.kwargs)
@inject(lambda ctx, result: setattr(ctx.artifacts, 'asset', result))
def make_new_asset(type, name, template):
    '''Make new asset'''

    construct = context.construct
    path_template = construct.get_path_template('asset')
    asset_path = path_template.format(
        project=context.project.path,
        asset_type=type,
        asset=name
    )

    if os.path.exists(asset_path):
        raise OSError('Asset already exists: ' + name)

    if template is not None:
        template_entry = construct.get_template('asset', name=template)
        if not template_entry:
            raise ConstructError('Asset template does not exist: ' + template)
        asset = template_entry.copy(asset_path)
    else:
        asset = fsfs.get_entry(asset_path)
        asset.tag('asset')

    return asset