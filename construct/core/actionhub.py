# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from collections import defaultdict
import fnmatch
from bisect import bisect_right
from fstrings import f
from construct.core.context import Context
from construct.core.action import Action
from construct.core.tasks import Task
from construct.core.signal import SignalHub
from construct.compat import basestring
from construct.core.util import ensure_type, ensure_instance
from construct.err import (
    RegistrationError, ConnectError, ActionUnavailable
)
__all__ = ['ActionHub', 'ActionAlias']


class ActionHub(object):
    '''Maintains a registry mapping Tasks to Actions. Tasks can be
    connected using the string attribute :attr:`Action.identifier` so that we
    can connected to :class:`Action` before the :class:`Action` is actually
    registered.
    '''

    def __init__(self):
        self._tasks = defaultdict(list)
        self._task_keys = defaultdict(list)
        self._actions = {}
        self._aliases = {}
        self._signals = SignalHub()
        self._make_context = self._signals.signal('make.context')

    def __repr__(self):
        return f('{self.__class__.__name__}()')

    def __call__(self, identifier, *args, **kwargs):
        action_type = self.get_action(identifier)
        ctx = self.make_context()
        action = action_type(ctx)
        return action

    def make_context(self):
        '''Chain make.context retrieving a :class:`Context` instance.'''

        ctx = Context()
        self._make_context.chain(ctx)
        return ctx

    def alias(self, identifier):
        if identifier not in self._aliases:
            self._aliases[identifier] = ActionAlias(self, identifier)
        return self._aliases.get(identifier)

    @property
    def aliases(self):
        return dict(self._aliases)

    def get_action(self, identifier):
        return self._actions[identifier]

    def get_actions(self, context=None):
        '''Get a dict containing all actions available in the given context.

        Arguments:
            identifier (str): Action identifier
            context (Context): Optional Context for lookup

        Returns:
            Dict[str, Action]
        '''

        if context is None:
            return dict(self._actions)

        ensure_instance(context, Context)

        return {
            action.identifier: action for action in self._actions.values()
            if action.available(context)
        }

    def get_tasks(self, identifier, context=None):
        '''Get a list of all available tasks for the given action identifier
        and context.

        Arguments:
            identifier (str): Action identifier
            context (Context): Optional Context for lookup

        Returns:
            List[Task]
        '''

        ensure_instance(identifier, basestring)

        tasks = list(self._tasks[identifier])
        task_keys = list(self._task_keys[identifier])
        for key in self._tasks.keys():
            if key == identifier:
                continue
            if fnmatch(identifier, key):
                objs_priorities = zip(
                    self._tasks[key],
                    self._task_keys[key]
                )
                for obj, priority in objs_priorities:
                    index = bisect_right(task_keys, priority)
                    tasks.insert(index, obj)
                    task_keys.insert(index, obj)

        iter_prepped = (self._prepare_task(t) for t in tasks)
        if context is None:
            return list(iter_prepped)

        return [t for t in iter_prepped if t._available(context)]

    def register(self, action):
        '''Register an action

        Arguments:
            action (Action): :class:`Action` type to register

        Returns:
            ActionAlias

        Raises:
            RegistrationError: When argument is not an :class:`Action` type
            ValueError: When action is already registered
        '''

        ensure_type(action, Action, RegistrationError)

        if action.identifier in self._actions:
            raise RegistrationError(
                'Action already registered: ', action.identifier
            )

        self._actions[action.identifier] = action
        return self.alias(action.identifier)

    def unregister(self, action):
        '''Unregister an action

        Arguments:
            action (Action): :class:`Action` type to register
        '''

        ensure_type(action, Action, RegistrationError)

        self._actions.pop(action.identifier, None)

    def connect(self, identifier, task):
        '''Connect a Task to an Action. When the Action is run the Task
        will be queued for execution.

        Arguments:
            identifier (str): :meth:`Action.identifier`
            task (Task): object to connect
        '''

        ensure_instance(identifier, basestring)
        ensure_instance(task, Task)

        if task in self._tasks[identifier]:
            return

        if not self._tasks[identifier]:
            self._tasks[identifier].append(task)
            self._task_keys[identifier].append(task.priority)
            return

        index = bisect_right(self._task_keys[identifier], task.priority)
        self._tasks[identifier].insert(index, task)
        self._task_keys[identifier].insert(index, task.priority)

    def disconnect(self, identifier, task):
        '''Disconnect a Task from an Action.

        Arguments:
            identifier (str): :meth:`Action.identifier`
            task (Task): object to disconnect
        '''

        ensure_instance(identifier, basestring)
        ensure_instance(task, Task)

        index = self._tasks.index(task)
        self._tasks[identifier].pop(index)
        self._task_keys[identifier].pop(index)

    def clear(self, identifier=None):
        '''Disconnect Tasks from an Action identifier.
        If no identifier is passed, disconnect all Tasks and unregister all
        Actions.

        Arguments:
            identifer (str): Optional :meth:`Action.identifier`
        '''

        if not identifier:
            self._tasks = defaultdict(list)
            self._task_keys = defaultdict(list)
            self._actions.clear()
            self._aliases.clear()
            return

        ensure_instance(identifier, basestring)

        self._tasks[identifier].clear()
        self._task_keys[identifier].clear()


class ActionAlias(object):
    '''Alias for an action available through an action_hub. This allows you
    to provide a shortcut to sending an action.

    instead of:

        action_hub.connect('action.identifier', function)
        action_hub('action.identifier', *args, **kwargs)

    do:

        action = ActionAlias(action_hub, 'action.identifier')
        action.connect(function)
        action(*args, **kwargs)

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

    def __call__(self, *args, **kwargs):
        return self.hub(self.identifier, *args, **kwargs)

    @property
    def action(self):
        return self.hub.get_action(self.identifier)

    @property
    def registered(self):
        return self.identifier in self.hub._actions

    def tasks(self, context=None):
        return self.hub.tasks(self.identifier, context=None)

    def connect(self, obj, **kwargs):
        return self.hub.connect(self.identifier, obj, **kwargs)

    def disconnect(self, obj):
        return self.hub.disconnect(self.identifier, obj)

    def clear(self):
        return self.hub.clear(self.identifier)

    # TODO: Add alias methods
