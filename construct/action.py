# -*- coding: utf-8 -*-
from __future__ import absolute_import

__all__ = [
    'Action',
    'ActionCollector',
    'ActionProxy',
    'get_action_identifier',
    'group_actions',
    'is_action',
    'is_action_type',
    'sort_actions',
]

import abc
import logging
from operator import attrgetter
from collections import OrderedDict
from construct import types, actionparams, signals
from construct.compat import basestring
from construct.constants import ACTION_SIGNALS
from construct.utils import missing, classproperty
from construct.actionrunner import ActionRunner
from construct.tasks import sort_tasks, CtxAction
from construct.errors import ActionUnavailable


_log = logging.getLogger(__name__)


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
                'label': 'Str Param',
                'type': str,
                'required': True,
            },
            'int_param': {
                'label': 'Int Param',
                'type': int,
                'required': False,
                'default': 1
            },
            ...
        }

    '''

    runner_cls = ActionRunner
    parameters = None
    suppress_signals = False

    @abc.abstractproperty
    def label(self):
        return NotImplemented

    @abc.abstractproperty
    def identifier(self):
        return NotImplemented

    @classproperty
    def description(cls):
        return cls.__doc__.split('\n')[0]

    @classproperty
    def long_description(cls):
        from textwrap import dedent
        lines = cls.__doc__.split('\n')
        first = lines[0] + '\n'
        rest = ''
        if len(lines) > 1:
            rest = dedent('\n'.join(lines[1:]))
        return first + rest

    def _returns(self):
        '''Called by ActionProxy to extract a return value from the Action's
        Context after run. This function calls Action.returns passing along
        the ActionContext when available. If Action.returns is not set
        all the artifacts from an Action run are returned.

        Examples:

            from construct import Action
            from construct.tasks import artifact

            class NewProject(Action):
                ...
                returns = artifact('project')
        '''

        return_getter = getattr(self, 'returns', None)
        if return_getter:
            if isinstance(return_getter, CtxAction):
                return return_getter.get(self.ctx)
            else:
                return return_getter(self.ctx)
        else:
            return self.ctx.artifacts

    @classmethod
    def _available(cls, ctx=missing):
        if ctx is missing:
            return True
        if callable(cls.available):
            return cls.available(ctx)
        return cls.available

    @abc.abstractmethod
    def available(ctx):
        '''
        Return True if this action is available in the provided Context. Must
        be a classmethod or staticmethod.

        Arguments:
            ctx (Context): Context class
        '''

    @classmethod
    def params(cls, ctx):
        if callable(cls.parameters):
            return cls.parameters(ctx)
        return cls.parameters or {}

    def __init__(self, *args, **kwargs):
        from construct.api import get_context
        from construct.actioncontext import ActionContext

        # Get base context to build ActionContext from
        ctx = kwargs.pop('ctx', get_context())

        # Validate params
        params = self.params(ctx)
        actionparams.validate(params)

        # Combine kwargs with action parameter defaults
        action_kwargs = actionparams.get_defaults(params)
        action_kwargs.update(kwargs)

        # Create action context
        self.ctx = ActionContext(self, args, action_kwargs, ctx)

        # Validate kwargs against params
        actionparams.validate_kwargs(params, self.ctx.kwargs)

        # Create action runner
        self.runner = self.runner_cls(self, self.ctx)

    def __call__(self):
        return self.runner.run()

    def __getattr__(self, attr):
        return self.ctx.__dict__.get(attr)

    def retry_group(self, priority):
        with signals.suppressed_when(self.suppress_signals, *ACTION_SIGNALS):
            return self.runner.retry_group(priority)

    def run_group(self, priority):
        with signals.suppressed_when(self.suppress_signals, *ACTION_SIGNALS):
            return self.runner.run_group()

    def run(self):
        with signals.suppressed_when(self.suppress_signals, *ACTION_SIGNALS):
            return self.runner.run()


def is_action_type(obj):
    return (
        obj is not Action and
        isinstance(obj, type) and
        issubclass(obj, Action)
    )


def is_action(obj):
    return isinstance(obj, Action)


def get_action_identifier(action_or_identifier):

    identifier = getattr(action_or_identifier, 'identifier', None)
    if identifier:
        return identifier

    if isinstance(action_or_identifier, basestring):
        return action_or_identifier

    raise RuntimeError(
        'Can not determine identifier of %s' % action_or_identifier
    )


class ActionCollector(object):
    '''Collects Actions and their associated tasks from the currently
    available Extensions.
    '''

    def __init__(self, extension_collector):
        self._extensions = extension_collector

    def __iter__(self):
        for action in sort_actions(self.collect().values()):
            yield action

    def __getattr__(self, identifier):
        return self.get(identifier)

    def get(self, identifier, ctx=None):
        from construct.api import get_context
        ctx = ctx or get_context()
        try:
            action = self.collect(missing)[identifier]
        except KeyError:
            _log.error('Action not found: %s', identifier)
            return
        else:
            if not action._available(ctx):
                raise ActionUnavailable('Action unavaibale in current context')
            return action

    def collect(self, ctx=None):
        '''Collect all actions in the given context. If no context is provided
        return ALL actions.

        Arguments:
            ctx: Context instance - used to determine action availability

        Returns:
            dict - (Action.identifier, Action) key value pairs
        '''

        from construct.api import get_context
        ctx = ctx or get_context()
        actions = {}
        for name, extension in self._extensions.by_name.items():
            if extension.enabled and extension._available(ctx):
                ext_actions = extension.get_actions(ctx)
                for identifier, action in ext_actions.items():
                    if identifier in actions:
                        _log.warning(
                            'Action identifier collision: %s <-> %s',
                            actions[identifier], action
                        )
                    else:
                        actions[identifier] = action

        return actions

    def collect_tasks(self, action_or_identifier, ctx=None):
        '''Collect all the tasks for a given Action or Action identifier.

        Arguments:
            action_or_identifier: Action class or Action.identifier string
            ctx: Context instance

        Returns:
            [Task...] - List of Task instances in priority order
        '''

        from construct.api import get_context
        ctx = ctx or get_context()
        identifier = get_action_identifier(action_or_identifier)

        tasks = []
        for name, extension in self._extensions.by_name.items():
            if extension.enabled and extension._available(ctx):
                more_tasks = extension.get_tasks(identifier, ctx)
                tasks.extend(more_tasks)

        return sort_tasks(tasks)


class ActionProxy(object):
    '''Proxy object that allows you to call Actions as if they were functions.
    '''

    def __init__(self, identifier):
        self.identifier = identifier

    @property
    def action(self):
        from construct import actions
        return actions.get(self.identifier)

    def instance(self, **kwargs):
        return self.action(**kwargs)

    def __repr__(self):
        return repr(self.action)

    def __str__(self):
        return str(self.action)

    def __getattr__(self, attr):
        return getattr(self.action, attr)

    def __call__(self, **kwargs):
        a = self.action(**kwargs)
        a.run()
        return a._returns()


def sort_actions(actions):
    '''Sort the given actions by identifier'''

    return sorted(actions, key=attrgetter('identifier'))


def group_actions(actions):
    '''Group sorted actions in a tree structure.

    Returns:
        OrderedDict suitable for creating a nested menu
    '''

    if isinstance(actions, dict):
        actions = sort_actions(actions.values())
    else:
        actions = sort_actions(actions)

    groups = OrderedDict()
    for action in actions:
        parts = action.identifier.split('.')
        if len(parts) == 1:
            groups.setdefault('', [])
            groups[''].append(action)
        else:
            nodes = parts[:-1]
            section = None
            for node in nodes:
                if section is None:
                    section = groups.setdefault(node, OrderedDict())
                    section.setdefault('', [])
                else:
                    section = section.setdefault(node, OrderedDict())
                    section.setdefault('', [])
            section[''].append(action)

    return groups
