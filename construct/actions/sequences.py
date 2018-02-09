# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import shutil
from construct.action import Action
from construct.tasks import task, extract, inject, requires
import fsfs
from construct.context import context


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
@extract(lambda ctx: ctx.kwargs)
@inject(lambda ctx, result: setattr(ctx.artifacts, 'sequence', result))
def make_new_sequence(name, template):
    '''Make new sequence'''

    construct = context.construct
    path_template = construct.get_path_template('sequence')
    sequence_path = path_template.format(
        project=context.project.path,
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
