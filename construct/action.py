# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

__all__ = ['Action']

import abc
from construct import types
from construct.actionloop import ActionLoop
from construct import actionparams


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

    _loop_class = ActionLoop
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

    @classmethod
    def params(cls, ctx):
        if callable(cls.parameters):
            return cls.parameters(ctx)
        return cls.parameters

    def __init__(self, ctx):
        actionparams.validate_kwargs(self.params(ctx), ctx.kwargs)
        self.ctx = ctx
        self.loop = self._loop_class(self, ctx)

    def __getattr__(self, attr):
        return self.ctx.__dict__.get(attr)

    def run_group(self, *args, **kwargs):
        return self.loop.run_group(*args, **kwargs)

    def run_next(self, *args, **kwargs):
        return self.loop.run_next(*args, **kwargs)

    def run(self, *args, **kwargs):
        return self.loop.run(*args, **kwargs)
