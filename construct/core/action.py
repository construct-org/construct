# -*- coding: utf-8 -*-
from __future__ import absolute_import
import abc
import sys
from itertools import groupby
from collections import OrderedDict, namedtuple
from construct.core import actionparams
from construct.err import ActionError
from construct.core import signals
__all__ = ['Action', 'is_action']


Result = namedtuple('Result', 'value failed exc ')


ABC = abc.ABCMeta('ABC', (object,), {})


class Action(ABC):
    '''Action Base Class

    Attributes:
        label (str): Nice name used for labeling like: 'New Project'
        description (str): Description of what the action does
        identifier (str): Used to find and run the action like: 'new.project'
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

        store (dict): Data stored by subscribers during action run
        artifacts (list): List of artifacts created during action run
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
    def is_available(context):
        '''
        Return True if this action is available in the provided Context. Must
        be a staticmethod.

        Arguments:
            context (Context): Context class
        '''

    def __init__(self, context, subscribers, **kwargs):
        actionparams.validate_kwargs(self.parameters, kwargs)

        self.context = context
        self.subscribers = subscribers
        self.subscribers_by_label = {s.label: s for s in subscribers}
        self.kwargs = kwargs
        self._init()

    def _init(self):
        self.running = False
        self.done = False
        self.failed = False
        self.priority = -1
        self.step = None
        self.step_index = -1
        self.exc = None
        self.store = {}
        self.artifacts = {}
        self.stack = OrderedDict((k, list(v)) for k, v in groupby(
            self.subscribers,
            key=lambda s: s.priority
        ))
        self.results = OrderedDict()
        signals.action_init.send(self)

    reset = _init

    def __iter__(self):
        '''Iterate over priority stack'''

        for priority, group in self.stack.items():
            yield priority, group

    def _ok_to_send(self):
        if self.done:
            raise ActionError(
                'Action already sent. Call action.reset first.'
            )
        if self.failed:
            raise ActionError(
                'Action already failed. Call action.reset first.'
            )
        if self.priority > -1:
            raise ActionError(
                'Action has already partially run.'
            )

    def set_ready(self):
        signals.action_ready.send(self)
        self.running = True

    def set_done(self):

        self.step = None
        self.step_index = -1
        self.running = False
        self.done = True
        signals.action_done.send(self)

    def run(self, continue_on_error=False):
        '''Send to all subscribers in order of priority.'''

        self._ok_to_send()
        self.set_ready()

        for i, (priority, subscribers) in enumerate(self.stack.items()):
            self.run_group(priority, subscribers, continue_on_error)

        self.set_done()

    def run_group(self, priority, group, continue_on_error=True):
        '''Send one priority group'''

        self.priority = priority
        self.running = True
        signals.action_group_ready.send(self)

        for subscriber in group:
            self.run_one(subscriber, continue_on_error)

        signals.action_group_done.send(self)

    def run_one(self, subscriber, continue_on_error=False):
        '''Send to just one subscriber'''

        self.step = subscriber
        self.step_index = self.subscribers.index(self.step)
        signals.action_step_ready.send(self)

        try:
            result = subscriber(self)
            self.results[subscriber.label] = Result(result, False, None)
        except:
            exc = sys.exc_info()
            self.exc = exc
            self.failed = True
            self.results[subscriber.label] = Result(None, True, exc)
            signals.action_error.send(self)
            if not continue_on_error:
                self.running = False
                raise

        signals.action_step_done.send(self)


def is_action(obj):
    '''Determine whether obj is an Action subclass or instance'''

    try:
        return issubclass(obj, Action)
    except Exception:
        return isinstance(obj, Action)
    except:
        return False
