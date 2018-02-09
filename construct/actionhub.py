# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

__all__ = ['ActionHub', 'ActionAlias']

from fnmatch import fnmatch
from operator import attrgetter
from collections import defaultdict, OrderedDict
from itertools import groupby
from bisect import bisect_right
from fstrings import f
from construct import types, actionparams
from construct.context import Context
from construct.action import Action
from construct.tasks import Task
from construct.signal import Channel
from construct.constants import *
from construct.compat import basestring
from construct.util import ensure_type, ensure_instance
from construct.err import (
    RegistrationError, ConnectError, ActionUnavailable
)


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
        self.channel = Channel()

    def __repr__(self):
        return f('{self.__class__.__name__}()')

    def __call__(self, identifier, *args, **kwargs):
        ctx = self._setup_action_context(identifier, *args, **kwargs)
        action = ctx.action_type(ctx)
        return action

    def _setup_action_context(self, identifier, *args, **kwargs):
        '''Chain setup.context retrieving a :class:`Context` instance.'''

        ctx = Context()
        self.channel.send('setup.context', ctx)
        ctx.action_hub = self
        ctx.action_type = self.get_action(identifier, ctx)
        ctx.tasks = self.get_tasks(identifier, ctx)
        ctx.tasks_by_name = {t.identifier: t for t in ctx.tasks}
        ctx.task_groups = OrderedDict(
            sorted((k, list(v)) for k, v in groupby(
                ctx.tasks,
                key=attrgetter('priority')
            ))
        )
        ctx.priorities = ctx.task_groups.keys()
        ctx.store = types.Namespace()
        ctx.artifacts = types.Namespace()
        ctx.args = args
        ctx.status = WAITING
        ctx.results = OrderedDict(
            (t.identifier, None) for t in ctx.tasks
        )
        ctx.requests = {}

        default_kwargs = actionparams.get_defaults(ctx.action_type.params(ctx))
        default_kwargs.update(kwargs)
        ctx.kwargs = kwargs

        return ctx

    def alias(self, identifier):
        if identifier not in self._aliases:
            self._aliases[identifier] = ActionAlias(self, identifier)
        return self._aliases.get(identifier)

    @property
    def aliases(self):
        return dict(self._aliases)

    def get_action(self, identifier, context=None):
        '''Get an action by identifier.

        Arguments:
            identifier (str): :attr:`Action.identifier`
            context (Context): Context to check for action availability

        Returns:
            Action

        Raises:
            ActionUnavailable when action is not available in the specified ctx
        '''
        try:
            action = self._actions[identifier]
        except KeyError:
            raise KeyError(f('KeyError: {identifier} has not been registered'))

        if context and not action.available(context):
            raise ActionUnavailable(f('{action} unavailable in {context}'))

        return action

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
        return tasks

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
        # TODO: Defer params dict validation until after registration
        actionparams.validate(action.params(Context()))

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

        index = self._tasks[identifier].index(task)
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

        self._tasks[identifier][:] = []
        self._task_keys[identifier][:] = []


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

    def __init__(self, action_hub, identifier):
        self.action_hub = action_hub
        self.identifier = identifier

    def __repr__(self):
        return f(
            '<{self.__class__.__name__}>('
            'action_hub={self.action_hub}, '
            'identifier={self.identifier}'
            ')'
        )

    def __call__(self, *args, **kwargs):
        return self.action_hub(self.identifier, *args, **kwargs)

    @property
    def action(self):
        return self.action_hub.get_action(self.identifier)

    @property
    def registered(self):
        return self.identifier in self.action_hub._actions

    def tasks(self, context=None):
        return self.action_hub.tasks(self.identifier, context=None)

    def connect(self, obj, **kwargs):
        return self.action_hub.connect(self.identifier, obj, **kwargs)

    def disconnect(self, obj):
        return self.action_hub.disconnect(self.identifier, obj)

    def clear(self):
        return self.action_hub.clear(self.identifier)

    # TODO: Add alias methods
