# -*- coding: utf-8 -*-
from __future__ import absolute_import
import abc
from construct.core import types
__all__ = ['Action']


class Action(types.ABC):
    '''Action Base Class

    Attributes:
        label (str): Nice name used for labeling like: 'New Project'
        identifier (str): Used to find and run the action like: 'new.project'
        description (str): Description of what the action does
        parameters (dict or staticmethod): Description of parameters for
        validation like:

        {
            'str_param': {
                'name': 'Str Param',
                'type': str,
                'required': True,
            },
            'int_param': {
                'name': 'Int Param',
                'type': int,
                'required': False,
                'default': 1
            },
            ...
        }

    '''

    parameters = {}

    @abc.abstractproperty
    def label(self):
        pass

    @abc.abstractproperty
    def description(self):
        pass

    @abc.abstractproperty
    def identifier(self):
        pass

    @abc.abstractmethod
    def available(ctx):
        '''
        Return True if this action is available in the provided Context. Must
        be a staticmethod.

        Arguments:
            ctx (Context): Context class
        '''

    def params(self, ctx):
        if callable(self.parameters):
            return self.params(ctx)
        return self.parameters

    def __init__(self, ctx):
        self.ctx = ctx
        self.event_loop = ActionEventLoop(self, ctx)


class ActionEventLoop(object):
    '''An event loop that runs an Action objects tasks for a given context.
    ActionEventLoop can be paused, resumed, stepped through, retried, or run
    all at once.
    '''

    def __init__(self, action, ctx):
        self.action = action
        self.ctx = ctx
