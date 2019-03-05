# -*- coding: utf-8 -*-
import os
import subprocess
import logging
import sys

platform = sys.platform.rstrip('1234567890')
if platform == 'darwin':
    platform = 'mac'

from past.types import basestring
from .. import context, schemas
from ..extensions import Extension, Action, Setting
from ..utils import get_lib_path


_log = logging.getLogger(__name__)


class Software(Extension):

    identifier = 'Launch'
    label = 'Launch Software'
    software = Setting('software')

    def is_available(self, ctx):
        return ctx.get('project', False)

    def get_launch_actions(self, ctx):

        actions = []
        file = ctx.get('file', None) or ''
        ext = os.path.splitext(file)[-1]

        for software_key in ctx['project']['software']:
            try:
                software = self.software[software_key]
            except KeyError:
                _log.error('Missing software config for: ' + software_key)

            if file and ext not in software['extensions']:
                continue

            actions.append(new_launch_action(software))

        return actions

    def get_actions(self, ctx):
        return self.get_launch_actions(ctx)


class LaunchAction(Action):

    software = None

    def get_command(self):
        cmd = self.software['cmd'][platform]
        if isinstance(cmd, basestring):
            if os.path.isfile(cmd):
                return True, cmd
        for item in cmd:
            if os.path.isfile(item):
                return True, item
        return False, cmd

    def get_software_env(self, ctx):
        env = os.environ.copy()
        update_values(env, **context.to_envvars(ctx))
        update_values(env, **self.software['env'])
        update_values(
            env,
            CONSTRUCT_HOST=self.software['host'],
            PYTHONPATH=[get_lib_path()]
        )
        return env

    def run(self, ctx, *args):
        found, cmd = self.get_command()
        if not found:
            raise OSError(
                "Can not find executable. "
                "Are you sure it's installed?"
            )

        cmd = [cmd] + self.software.get('args', [])
        if args:
            cmd += list(args)
        kwargs = dict(env=self.get_software_env(ctx))

        # TODO: Create workspace if it doesn't exist and we are launching
        #       in the context of a task.

        _log.debug('Launching %s' % self.software['name'].title())
        run(cmd, **kwargs)


def new_launch_action(software):
    '''Create a new LaunchAction for a piece of software.'''

    return type(
        'Launch' + software['name'].title(),
        (LaunchAction,),
        dict(
            identifier='launch.' + software['name'],
            label='Launch ' + software['label'],
            icon=software['icon'],
            software=software
        )
    )


def run(*args, **kwargs):
    '''On Windows start a detached process in it's own process group.'''

    if platform == 'win':
        create_new_process_group = 0x00000200
        detached_process = 0x00000008
        creation_flags = detached_process | create_new_process_group
        kwargs.setdefault('creationflags', creation_flags)

    kwargs.setdefault('shell', True)
    subprocess.Popen(*args, **kwargs)


def update_values(d, **values):
    for k, v in values.items():
        update_value(d, k, v)


def update_value(d, k, v):
    if isinstance(v, basestring):
        d[k] = v
    elif isinstance(v, list):
        v = os.pathsep.join(v)
        if k not in v:
            d[k] = v
        else:
            d[k] = os.pathsep.join([v, d[k]])
    else:
        d[k] = str(v)
