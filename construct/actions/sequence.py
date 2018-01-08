# -*- coding: utf-8 -*-
from __future__ import absolute_import
import fsfs
from construct.core.action import Action
from construct.core.actionrouter import action_router


class NewSequence(Action):

    label = 'New Sequence'
    identifier = 'new.sequence'
    parameters = dict(
        root={
            'label': 'Sequence Root',
            'required': True,
            'type': str
        }
    )
    description = 'Create a new sequence'

    @staticmethod
    def is_available(context):
        return True


def new_sequence(root):
    entry = fsfs.Entry(root)
    entry.tag('sequence')
    return entry


new_sequence_step = action_router(
    new_sequence,
    extractor=lambda a: dict(root=a.kwargs['root']),
    injector=lambda a, r: a.artifacts.update({r.name: r})
)
