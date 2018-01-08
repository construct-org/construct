# -*- coding: utf-8 -*-
from __future__ import absolute_import
import getpass
import os
import sys
import fsfs
from fstrings import f
from construct.core.util import env_with_default, path_split
from construct.core import plugins, context
from construct.core.actionhub import ActionHub
from construct import actions
from construct.err import RegistrationError


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
        self.action_hub = ActionHub(self)

        # Action aliases
        # Forward calls to action_hub
        self.new_project = self.action_hub.alias('new.project')
        self.new_asset = self.action_hub.alias('new.asset')
        self.new_task = self.action_hub.alias('new.task')
        self.new_sequence = self.action_hub.alias('new.sequence')
        self.new_shot = self.action_hub.alias('new.shot')
        self.new_workspace = self.action_hub.alias('new.workspace')

        # Initialize context and discover plugins
        self.context = context.from_env()
        if host:
            self.context.host = host
        if root:
            self.context.root = root

        self._register_builtins()
        self.discover_plugins()

    def get_context(self):
        return self.context

    def set_context(self, ctx):
        self.context = ctx

    def set_context_from_path(self, path):
        path_context = context.from_path(path)
        ctx = context.merge(
            self.context,
            path_context,
            exclude=['host', 'root']
        )
        self.set_context(ctx)

    def search(self, *args, **kwargs):
        '''Yield all entries matching the provided tags.

        Usage:

            cons = Construct()
            cons.search('asset')

        Arguments:
            *tags (List[str]): List of tags to match [Optional]
            direction (0 or 1): fsfs.DOWN or fsfs.UP
            root (str): Directory to start search from. Defaults to
                :attr:`context.root`
            name (str): Name to search for [Optional]

        See also:
            :meth:`fsfs.search`
        '''
        kwargs.setdefault('root', self.context.root or os.getcwd())

        for entry in fsfs.search(*args, **kwargs):
            yield entry

    def one(self, *args, **kwargs):
        '''Find one entry matching the provided tags.

        Usage:

            cons = Construct()
            cons.one('project', name='MyProject')

        Arguments:
            *tags (List[str]): List of tags to match [Optional]
            direction (0 or 1): fsfs.DOWN or fsfs.UP
            root (str): Directory to start search from. Defaults to
                :attr:`context.root`
            name (str): Name to search for [Optional]

        See also:
            :meth:`fsfs.one`
        '''
        kwargs.setdefault('root', self.context.root or os.getcwd())

        return fsfs.one(*args, **kwargs)

    def _register_builtins(self):
        '''Register builtin actions'''
        actions.register(self)

    def _unregister_builtins(self):
        '''Unregister builtin actions'''
        actions.unregister(self)

    def discover_plugins(self):
        '''Discover and register available plugins. Searches the "construct"
        distutils entry_point as well as the paths defined by the env var
        CONSTRUCT_PLUGIN_PATH'''

        self.plugins = plugins.discover(*self.plugin_paths)
        for name, plugin in self.plugins.items():
            plugin.enabled = False
            if plugin.is_available(self.context):
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
