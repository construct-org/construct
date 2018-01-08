# -*- coding: utf-8 -*-
from __future__ import absolute_import
from fstrings import f

__all__ = ['ActionAlias']


class ActionAlias(object):
    '''Alias for an action available through an action_hub. This allows you
    to provide a shortcut to sending an action.

    instead of:

        action_hub.subscribe('action.identifier', function)
        action_hub.send('action.identifier', **kwargs)

    do:

        action = ActionAlias(action_hub, 'action.identifier')
        action.subscribe(function)
        action(**kwargs)

    Many action aliases are provided on a :class:`Construct` instance like:
    new_project, new_asset, new_task, new_sequence, new_shot...
    '''

    def __init__(self, action_hub, action_identifier):
        self.action_hub = action_hub
        self.action_identifier = action_identifier

    def __repr__(self):
        return f(
            '<{self.__class__.__name__}>('
            'action_hub={self.action_hub}, '
            'action_identifier={self.action_identifier}'
            ')'
        )

    def make(self, **kwargs):
        return self.action_hub.make(self.action_identifier, **kwargs)

    def run(self, **kwargs):
        return self.action_hub.run(
            self.action_identifier,
            **kwargs
        )

    __call__ = run

    def subscribe(self, *args, **kwargs):
        self.action_hub.subscribe(self.action_identifier, *args, **kwargs)

    def unsubscribe(self, *args, **kwargs):
        self.action_hub.unsubscribe(self.action_identifier, *args, **kwargs)
