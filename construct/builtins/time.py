# -*- coding: utf-8 -*-
from __future__ import absolute_import
from construct.action import Action
from construct.tasks import (
    task,
    pass_context,
    pass_kwargs,
    returns,
    artifact,
    store,
    params,
    success,
    requires
)
from construct import types, get_host, utils, get_path_template
from construct.vendor.lucidity.error import ParseError


class Save(Action):
    '''Save the frame range for this shot or asset'''

    label = 'Save Frame Range'
    identifier = 'time.saveframerange'

    @staticmethod
    def parameters(ctx):
        params = dict(
            asset_or_shot={
                'label': 'Asset or Shot',
                'required': True,
                'type': types.Entry,
                'help': 'Asset or Shot Entry'
            },
            min={
                'label': 'Min Frame',
                'required': True,
                'type': types.Number,
                'help': 'Min Frame'
            },
            start={
                'label': 'Start Frame',
                'required': False,
                'type': types.Number,
                'help': 'Animation Start Frame',
            },
            end={
                'label': 'End Frame',
                'required': False,
                'type': types.Number,
                'help': 'Animation End Frame',
            },
            max={
                'label': 'Max Frame',
                'required': True,
                'type': types.Number,
                'help': 'Max Frame'
            },
        )

        if not ctx:
            return params

        params['asset_or_shot']['default'] = ctx.asset or ctx.shot

        host = get_host()
        if host:
            frame_range = host.get_frame_range()

            if frame_range is NotImplemented:
                return params

            params['min']['default'] = float(frame_range[0])
            params['start']['default'] = float(frame_range[1])
            params['end']['default'] = float(frame_range[2])
            params['max']['default'] = float(frame_range[3])

        return params

    @staticmethod
    def available(ctx):
        return ctx.host and ctx.task


class Sync(Action):
    '''Sync your scenes frame range'''

    label = 'Sync Frame Range'
    identifier = 'time.syncframerange'

    @staticmethod
    def parameters(ctx):
        params = dict(
            asset_or_shot={
                'label': 'Asset or Shot',
                'required': True,
                'type': types.Entry,
                'help': 'Asset or Shot Entry'
            }
        )

        if not ctx:
            return params

        params['asset_or_shot']['default'] = ctx.asset or ctx.shot
        return params

    @staticmethod
    def available(ctx):
        return ctx.host != 'cli' and ctx.task


@task
@pass_kwargs
def store_frame_range(asset_or_shot, min, start, end, max):
    '''Stores the frame range in the asset or shot'''

    asset_or_shot.write(
        frame_range=[min, start, end, max]
    )


@task
@pass_kwargs
@pass_context
@returns(store('frame_range'))
def get_frame_range(ctx, asset_or_shot):
    '''Get the Asset or Shot frame range'''

    frame_range = asset_or_shot.data.get(
        'frame_range',
        ctx.project.data.get(
            'frame_range',
            [101, 101, 580, 580]
        )
    )
    return frame_range


@task
@requires(store('frame_range'))
@params(store('frame_range'))
@returns(artifact('frame_range'))
def apply_frame_range(frame_range):
    '''Applies the frame range to your current scene'''

    host = get_host()
    host.set_frame_range(*frame_range)
    return {'frame_range': frame_range}
