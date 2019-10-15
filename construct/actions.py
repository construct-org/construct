# -*- coding: utf-8 -*-

from __future__ import absolute_import

# Standard library imports
import inspect
import logging

# Third party imports
import entrypoints

# Local imports
from .constants import EXTENSIONS_ENTRY_POINT
from .schemas import new_validator
from .utils import iter_modules


__all__ = [
    'Action',
    'ActionManager',
    'is_action_type',
    'is_action',
]


_log = logging.getLogger(__name__)


class Action(object):
    '''The Action class allows users to extend Construct with their own
    behavior and functionality. When writing your own Actions use the
    `setup` method instead of `__init__` to perform any setup your Action
    requires like creating a database connection. The `load` method should be
    used to register event handlers and extend the base API. The `unload`
    method should be used to undo everything that was done in `load`.

    Actions commonly do the following:

     - Emit custom events
     - Provide event handlers
     - Provide Methods and Objects to extend the base API

    Look at construct.builtins to see the Actions that provide the core
    functionality of Construct.
    '''

    description = ''
    icon = ''
    identifier = ''
    label = ''
    menu = ''

    def __init__(self, api):
        self.api = api

    def __call__(self, *args, **kwargs):

        arguments = inspect.getcallargs(self.run, *args, **kwargs)

        # Create Cerberus Validator
        ctx = kwargs.pop('ctx', self.api.context.copy())
        v = new_validator(self.parameters(self.api, ctx))
        kwargs = v.validated(arguments)

        # TODO: Validate arguments
        try:
            return self.run(self.api)
        except Exception as e:
            # TODO: Raise an ActionError
            #       If gui show an error dialog.
            raise

    def parameters(self, api, ctx=None):
        '''Subclasses should implement return a Cerberus Validation Schema
        to validate arguments passed to the run method.
        '''
        return {}

    def run(self, *args, **kwargs):
        '''Subclasses should implement run to perform the Action's work.'''
        return NotImplemented

    def is_available(self, ctx):
        '''Return True if the Action is available in the given context'''
        return True


ACTION_TYPES = (Action,)


def is_action_type(obj):
    '''Check if an obj is an Action type.'''

    return (
        obj not in ACTION_TYPES and
        isinstance(obj, type) and
        issubclass(obj, ACTION_TYPES)
    )


def is_action(obj):
    '''Check if an obj is an Action instance.'''

    return isinstance(obj, ACTION_TYPES)


class ActionManager(dict):

    def __init__(self, api):
        self.api = api

    def load(self):
        '''Discover and load all Actions'''

    def unload(self):
        '''Unload all Actions'''
        self.clear()

    def register(self, action):
        '''Register an Action'''

        if self.loaded(action):
            _log.debug('Action already loaded: %s' % action)

        _log.debug('Loading action: %s' % action)
        if is_action_type(action):
            inst = action(self.api)
        elif is_action(action):
            inst = action
        else:
            _log.error('Expected Action type got %s' % action)
            return

        self[action.identifier] = inst

    def unregister(self, action):
        '''Unregister an Action'''

        identifier = getattr(action, 'identifier', action)
        self.pop(identifier, None)
        _log.debug('Unloading action: %s' % action)

    def loaded(self, action):
        '''Check if an Action has been loaded.'''

        identifier = getattr(action, 'identifer', action)
        return identifier in self

    def discover(self):
        '''Find and iterate over all Action subclasses

        1. Yields Builtin Actions
        2. Yields Actions registered to construct.actions entry_point
        2. Yields Actions in python files in CONSTRUCT_PATH
        3. Yields Actions in settings['actions']
        '''

        from .action import actions
        for action in actions:
            yield action

        from .hosts import actions
        for action in actions:
            yield action

        entry_points = entrypoints.get_group_all(EXTENSIONS_ENTRY_POINT)
        for entry_point in entry_points:
            obj = entry_point.load()
            for _, action in inspect.getmembers(obj, is_action_type):
                yield action

        action_paths = [p / 'actions' for p in self.path]
        for mod in iter_modules(*action_paths):
            for _, action in inspect.getmembers(mod, is_action_type):
                yield action

        for module_path in self.settings.get('actions', []):
            try:
                mod = __import__(module_path)
            except ImportError:
                _log.debug('Action module does not exist: ' + module_path)
            for _, action in inspect.getmembers(mod, is_action_type):
                yield action

    def ls(self, typ=None):
        '''Get a list of available actions.

        Arguments:
            typ (Action, Optional): List only a specific type of Action.

        Examples:
            ls()  # lists all actions
            ls(Host)  # list only Host actions
        '''

        matches = []
        for action in self.values():
            if not type or isinstance(action, typ):
                matches.append(action)
        return matches

    def get_available(self, ctx=None, typ=None):
        '''Get actions available in the provided contaction.'''

        ctx = ctx or self.api.context.copy()
        return [action for action in self.values() if action.is_available(ctx)]
