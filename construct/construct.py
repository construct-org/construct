# -*- coding: utf-8 -*-
from __future__ import absolute_import

__all__ = ['Construct']

import getpass
import os
import sys
from functools import wraps
import fsfs
from fstrings import f
from itertools import chain
from construct import plugins, context, actions, signal
from construct.util import env_with_default, path_split
from construct.actionhub import ActionHub
from construct.err import RegistrationError


# Decorators and convenience functions used on Construct object

def check_context(*predicates):
    def method_wrapper(meth):
        @wraps(meth)
        def method(self, *args, **kwargs):
            for predicate in predicates:
                okay, msg = predicate(self._ctx)
                if not okay:
                    raise ContextError(msg)
            return meth(self, *args, **kwargs)
        return method
    return method_wrapper


def contains_project(ctx):
    return ctx.project is not None, 'No project in current context.'


class Construct(object):

    def __init__(self, **kwargs):

        # Configuration
        host = kwargs.pop('host', None)
        root = kwargs.pop('root', None)
        defaults = dict(
            plugin_paths=env_with_default(
                'CONSTRUCT_PLUGIN_PATH',
                os.path.expanduser('~/.construct/plugins'),
                converter=path_split
            ),
            debug=env_with_default('CONSTRUCT_DEBUG', False, converter=int),
            user=env_with_default('CONSTRUCT_USER', getpass.getuser()),
        )
        if 'plugin_paths' in kwargs:
            defaults['plugin_paths'].extend(kwargs.pop('plugin_paths'))
        defaults.update(kwargs)
        self.__dict__.update(defaults)

        # Create action and event hub
        self.action_hub = ActionHub()
        self.action_hub.channel.connect('setup.context', self._setup_context)

        # Action aliases
        # Forward calls to action_hub
        self.new_project = self.action_hub.alias('new.project')
        self.new_asset = self.action_hub.alias('new.asset')
        self.new_task = self.action_hub.alias('new.task')
        self.new_sequence = self.action_hub.alias('new.sequence')
        self.new_shot = self.action_hub.alias('new.shot')
        self.new_workspace = self.action_hub.alias('new.workspace')

        # Initialize context and discover plugins
        self._ctx = context.from_env()
        if host:
            self._ctx.host = host
        if root:
            self._ctx.root = root
        self._ctx.construct = self

        self._plugins = {}
        self._templates = {}
        self._register_builtins()
        self._discover_plugins()

    def _setup_context(self, ctx):
        '''Injects current Contstruct Context into action context'''

        ctx.update(self._ctx)
        return ctx

    def available_actions(self):
        return self.action_hub.get_actions(self._ctx)

    def get_plugins(self):
        return self._plugins

    def get_context(self):
        return self._ctx

    def set_context(self, ctx):
        last_ctx = self._ctx
        self._ctx = ctx
        self._rediscover_plugins()
        signal.send('context.changed', self, last_ctx, self._ctx)

    def set_context_from_path(self, path):
        last_ctx = self._ctx
        path_ctx = context.from_path(path)
        self._ctx.update(path_ctx)
        self._rediscover_plugins()
        signal.send('context.changed', self, last_ctx, self._ctx)

    def context_from_path(self, path):
        return context.from_path(path)

    @check_context(contains_project)
    def get_path_template(self, name):
        '''Get one of the current projects templates by name'''

        try:
            return self._ctx.project.read('templates')[name]
        except:
            raise KeyError(f('KeyError: no template named {name}'))

    @check_context(contains_project)
    def get_path_templates(self):
        '''Get a dict containining the current projects templates'''

        return self._ctx.project.read('templates')

    def _template_search_paths(self):

        paths = []
        if self._ctx.project:
            paths.append(
                os.path.join(self._ctx.project.data.path, 'templates')
            )

        for name, plugin in self._plugins.items():
            paths.append(os.path.join(plugin.path, 'templates'))

        return [p for p in paths if os.path.isdir(p)]

    def get_template(self, tag, name=None):
        '''Get a template by tag and name. A template is a preset folder or
        file stored in your project .data/templates folder. They can be used
        to create new assets, sequences, shots, tasks, and workspaces'''

        # Lookup templates in project first

        search = chain(*(
            fsfs.search(path, tag, depth=1)
            for path in self._template_search_paths()
        ))

        names = []
        templates = []
        for entry in search:
            if entry.name in names:
                continue
            names.append(entry.name)
            templates.append(entry)

        if not name:
            return templates

        near_match = None
        for template in templates:
            if name == template.name:
                return template
            if name in template.name:
                near_match = template

        return near_match

    def search(self, *tags, **kwargs):
        '''Yield all entries matching the provided tags.

        Usage:

            cons = Construct()
            cons.search('asset')

        Arguments:
            *tags (str): List of tags to match [Optional]
            direction (0 or 1): fsfs.DOWN or fsfs.UP
            root (str): Directory to start search from. Defaults to
                :attr:`_ctx.root`
            name (str): Name to search for [Optional]

        See also:
            :meth:`fsfs.search`
        '''

        name = kwargs.pop('name', None)
        kwargs.setdefault('root', self._ctx.root or os.getcwd())
        kwargs.setdefault('tags', args or None)

        for entry in fsfs.search(**kwargs):
            if name:
                if name in entry.name:
                    yield entry
            else:
                yield entry


    def one(self, *tags, **kwargs):
        '''Find one entry matching the provided tags.

        Usage:

            cons = Construct()
            cons.one('project', name='MyProject')

        Arguments:
            *tags (str): List of tags to match [Optional]
            direction (0 or 1): fsfs.DOWN or fsfs.UP
            root (str): Directory to start search from. Defaults to
                :attr:`context.root`
            name (str): Name to search for [Optional]

        See also:
            :meth:`fsfs.search`
        '''

        name = kwargs.get('name', None)

        # If name is None just return the first search result or None
        if name is None:
            for entry in self.search(*args, **kwargs):
                return entry
            return

        # If name is not None return the entry whose name matches best
        best_match = None
        for entry in self.search(*tags, **kwargs):
            if name == entry.name:
                return entry
            if name in entry.name:
                best_match = entry
        return best_match

    def _register_builtins(self):
        '''Register builtin actions'''

        actions.register(self)

    def _unregister_builtins(self):
        '''Unregister builtin actions'''

        actions.unregister(self)

    def _discover_plugins(self):
        '''Discover and register available plugins. Searches the "construct"
        distutils entry_point as well as the paths defined by the env var
        CONSTRUCT_PLUGIN_PATH'''

        self._ctx.push()
        try:
            self._plugins = plugins.discover(*self.plugin_paths)
            for name, plugin in self._plugins.items():
                plugin.path = os.path.dirname(plugin.__file__)
                plugin.enabled = False
                if plugin.available(self._ctx):
                    plugin.enabled = True

                    try:
                        plugin.register(self)
                    except Exception:
                        exc_type, exc, tb = sys.exc_info()
                        new_exc = RegistrationError(f(
                            'Failed to register plugin {}: {}',
                            name,
                            exc or exc_type
                        ))
                        raise new_exc.__class__, new_exc, tb
        finally:
            self._ctx.pop()

    def _rediscover_plugins(self):
        self._unregister_builtins()
        self._unregister_plugins()
        self._plugins = {}
        self._templates = {}
        self._register_builtins()
        self._discover_plugins()

    def _unregister_plugins(self):
        self._ctx.push()
        try:
            while self._plugins:
                name, plugin = self._plugins.popitem()

                try:
                    plugin.unregister(self)
                except Exception:
                    exc_type, exc, tb = sys.exc_info()
                    new_exc = RegistrationError(f(
                        'Failed to unregister plugin {}: {}',
                        name,
                        exc or exc_type
                    ))
                    raise new_exc.__class__, new_exc, tb

                plugin.enabled = False

        finally:
            self._ctx.pop()
