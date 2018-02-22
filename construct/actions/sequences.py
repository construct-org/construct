# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import shutil
from construct.action import Action
from construct.tasks import task, pass_context, pass_kwargs, returns, artifact
import fsfs


class NewSequence(Action):

    label = 'New Sequence'
    identifier = 'new.sequence'
    description = 'Create a new Construct Sequence'
    parameters = dict(
        name={
            'label': 'Sequence Name',
            'required': True,
            'type': str,
            'help': 'Name of sequence',
        },
        template={
            'label': 'Sequence Template',
            'required': False,
            'type': str,
            'help': 'Name of sequence template'
        }
    )

    @staticmethod
    def available(ctx):
        return (
            ctx.project
            and not ctx.sequence
            and not ctx.shot
            and not ctx.asset
        )


@task
@pass_context
@pass_kwargs
@returns(artifact('sequence'))
def make_new_sequence(ctx, name, template):
    '''Make new sequence'''

    construct = ctx.construct
    path_template = construct.get_path_template('sequence')
    sequence_path = path_template.format(
        project=ctx.project.path,
        sequence=name
    )

    if os.path.exists(sequence_path):
        raise OSError('Sequence already exists: ' + name)

    if template is not None:
        template_entry = construct.get_template('sequence', name=template)
        if not template_entry:
            raise ConstructError('Seq template does not exist: ' + template)
        sequence = template_entry.copy(sequence_path)
    else:
        sequence = fsfs.get_entry(sequence_path)
        sequence.tag('sequence')

    return sequence
