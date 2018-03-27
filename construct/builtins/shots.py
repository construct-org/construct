# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import fsfs
from construct.action import Action
from construct.tasks import task, pass_context, pass_kwargs, returns, artifact


class NewShot(Action):

    label = 'New Shot'
    identifier = 'new.shot'
    description = 'Create a new Construct Shot'

    @staticmethod
    def parameters(ctx):
        params = dict(
            sequence={
                'label': 'Sequence',
                'required': True,
                'type': str,
                'help': 'Name of sequence',
            },
            name={
                'label': 'Shot',
                'required': True,
                'type': str,
                'help': 'Name of shot'
            },
            template={
                'label': 'Shot Template',
                'required': False,
                'type': str,
                'help': 'Name of shot template'
            }
        )

        if ctx and ctx.sequence:
            params['sequence']['default'] = ctx.sequence.name
            params['sequence']['required'] = False

        return params

    @staticmethod
    def available(ctx):
        return (
            ctx.project
            and not ctx.asset
            and not ctx.shot
        )


@task
@pass_context
@pass_kwargs
@returns(artifact('shot'))
def make_new_shot(ctx, sequence, name, template):
    '''Make new shot'''

    construct = ctx.construct
    sequence_path_template = construct.get_path_template('sequence')
    sequence_path = sequence_path_template.format(
        project=ctx.project.path,
        sequence=sequence
    )

    if not os.path.exists(sequence_path):
        raise OSError('Sequence does not exist: ' + sequence)

    shot_path_template = construct.get_path_template('shot')
    shot_path = shot_path_template.format(
        project=ctx.project.path,
        sequence=sequence,
        shot=name
    )

    if os.path.exists(shot_path):
        raise OSError('Shot already exists: ' + name)

    if template is not None:
        template_entry = construct.get_template('shot', name=template)
        if not template_entry:
            raise OSError('Seq template does not exist: ' + template)
        shot = template_entry.copy(shot_path)
    else:
        shot = fsfs.get_entry(shot_path)
        shot.tag('shot')

    return shot
