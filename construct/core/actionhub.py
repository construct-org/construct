# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from collections import defaultdict
import fnmatch
from bisect import bisect_right
from fstrings import f
from construct.core.action import Action
from construct.core.actionalias import ActionAlias
from construct.core import actionparams
from construct.core.priority import Priority
from construct.compat import basestring
from construct.core.util import ensure_type, ensure_callable, get_callable_name
from construct.err import (
    RegistrationError, SubscribeError, InvalidIdentifier, ActionUnavailable
)
__all__ = ['ActionHub']


class GetContext(Action):

    label = 'Get Context'
    identifier = 'get.context'
    parameters = {}
    description = 'Create a new Construct project'
    is_available = True


class ActionHub(object):
    ''':class:`Action` registry and dispatcher. Used to keep track of all
    available :class:`Action` types and their subscribers. Receivers can be
    connected using the string attribute :attr:`Action.identifier` so that we
    can connected to :class:`Action` before they are registered.
    '''

    def __init__(self, cons):
        self.cons = cons
        self._registry = defaultdict(list)
        self._actions = {}

    def __repr__(self):
        return f('<{self.__class__.__name__}>()')

    def __iter__(self):
        return sorted(self._actions.items())

    def get_context(self):
        '''Run GetContext action and return context artifact'''

        return self.cons.context

    def available_actions(self, context=None):
        '''Iterate over actions available in context'''

        context = context or self.get_context()

        actions = []
        for identifier, action in sorted(self._actions.items()):
            if is_available(action, context):
                actions.append((identifier, action))

        return actions

    def available_subscribers(self, action, context=None):
        '''Iterate over available subscribers'''

        context = context or self.get_context()

        identifier = get_identifier(action)
        if identifier is None:
            raise InvalidIdentifier(
                f('{action} is an invalid Action or identifier')
            )

        if '*' in identifier:  # Handle wildcard subscriptions
            all_subscribers = []
            for key in fnmatch.filter(self._registry.keys(), identifier):
                for subscriber in self._registry[key]:
                    if subscriber not in all_subscribers:
                        all_subscribers.append(subscriber)
        else:
            all_subscribers = self._registry[identifier]

        subscribers = []
        for subscriber in all_subscribers:
            if is_available(subscriber, context):
                subscribers.append(subscriber)

        return subscribers

    def register(self, action):
        '''Register an action.

        Arguments:
            action (Action): :class:`Action` instance
        '''

        ensure_type(action, Action, RegistrationError)
        actionparams.validate(action.parameters)

        identifier = get_identifier(action)
        if identifier is None:
            raise SubscribeError(
                f('"action" must be an Action or str: {action}')
            )

        if identifier in self._actions:
            return

        self._actions[identifier] = action

    def unregister(self, action):
        '''Unregister an action.

        Arguments:
            action (Action): :class:`Action` instance
        '''

        ensure_type(action, Action, RegistrationError)

        identifier = get_identifier(action)
        if identifier is None:
            raise SubscribeError(
                f('"action" must be an Action or str: {action}')
            )

        if identifier not in self._actions:
            return

        self._actions.pop(identifier)

    def subscribe(self, action, subscriber, priority=0, is_available=True):
        '''Subscribe a callable to an action and assign a priority. The
        priority determines the call order of the subscribers when an action
        is run.

        Arguments:
            action (Action or str): :class:`Action` instance or identifier str
            subscriber (Callable): Object to receive dispatched actions
            priority (int): Call priority of subscriber
        '''

        ensure_callable(subscriber, SubscribeError)
        identifier = get_identifier(action)
        if identifier is None:
            raise SubscribeError(
                f('"action" must be an Action or str: {action}')
            )

        if subscriber in self._registry[identifier]:
            return

        if not is_action_step(subscriber):
            subscriber = to_subscriber(
                subscriber,
                priority=priority,
                is_available=is_available
            )

        subscribers = self._registry[identifier]
        if not subscribers:
            subscribers.append(subscriber)
            return

        # Insert maintaining order by priority
        keys = [s.priority for s in self._registry[identifier]]
        index = bisect_right(keys, priority)
        subscribers.insert(index, subscriber)

    def unsubscribe(self, action, subscriber):
        '''Unsubscribe from an action.

        Arguments:
            action (Action or str): :class:`Action` instance or identifier str
            subscriber (Callable): Object to receiving dispatched actions
        '''

        identifier = get_identifier(action)
        if identifier is None:
            raise SubscribeError(
                f('"action" must be an Action or str: {action}')
            )

        if identifier not in self._registry:
            return

        if subscriber not in self._registry[identifier]:
            return

        self._registry[identifier].remove(subscriber)

    def _get_action(self, action):
        identifier = get_identifier(action)
        if identifier is None:
            raise InvalidIdentifier(
                f('{action} is an invalid Action or identifier')
            )

        action_type = self._actions.get(identifier, None)
        if action_type is None:
            raise InvalidIdentifier(
                f('{action} is not recognized among registered Actions')
            )
        return action_type

    def make(self, action, context=None, **kwargs):
        context = context or self.get_context()
        action_type = self._get_action(action)
        subscribers = self.available_subscribers(action, context)
        action = action_type(context, subscribers, **kwargs)
        return action

    def alias(self, identifier):
        return ActionAlias(self, identifier)

    def run(self, action, **kwargs):
        continue_on_error = kwargs.pop('continue_on_error', False)
        action = self.make(action, **kwargs)
        if action.subscribers is None:
            return
        action.run(continue_on_error=continue_on_error)
        return action


def get_identifier(action):
    '''Get identifier from string or Action instance

    Arguments:
        action (Action or str): Action instance or identifier string

    Returns:
        str: :attr:`Action.identifier` or unmodified action argument
    '''

    if isinstance(action, basestring) and action:
        return action
    if isinstance(action, Action) or issubclass(action, Action):
        return action.identifier


class SubscriberProxy(object):

    def __init__(self, obj):
        self.obj = obj
        self.label = None
        self.description = None
        self.priority = None
        self.enabled = None
        self.is_available = None

    def __call__(self, *args, **kwargs):
        return self.obj(*args, **kwargs)

    def __hash__(self):
        return hash(self.obj)

    def __eq__(self, other):
        if isinstance(other, SubscriberProxy):
            return self.obj is other.obj
        return self.obj is other


def to_subscriber(obj, priority=0, is_available=True):
    '''Ensures that obj has a label, description and priority

    Arguments:
        obj (Callable): object to decorate, usually a function
        priority (int): default priority
        is_available (bool or callable): default availability

    Returns:
        obj: with added attributes
    '''

    proxy = SubscriberProxy(obj)
    proxy.label = getattr(obj, 'label', None) or get_callable_name(obj)
    proxy.description = getattr(obj, 'description', None) or obj.__doc__
    proxy.priority = getattr(obj, 'priority', None) or priority
    if not isinstance(proxy.priority, Priority):
        proxy.priority = Priority(priority)
    proxy.enabled = getattr(obj, 'enabled', None) or True
    proxy.is_available = getattr(obj, 'is_available', None) or is_available
    return proxy


def is_action_step(obj):
    '''Test whether or not an obj is a valid action step.'''

    if not hasattr(obj, 'label'):
        return False
    if not hasattr(obj, 'description'):
        return False
    if not hasattr(obj, 'priority'):
        return False
    if not hasattr(obj, 'is_available'):
        return False
    return True


def is_available(action_or_step, context):
    '''Test whether an action or action_step is available in context'''

    if callable(action_or_step.is_available):
        return action_or_step.is_available(context)
    return action_or_step.is_available
