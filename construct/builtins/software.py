# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import subprocess
import logging
import sys

platform = sys.platform.rstrip('1234567890')
if platform == 'darwin':
    platform = 'mac'

from past.types import basestring
from .. import context, schemas
from ..extensions import Extension
from ..utils import get_lib_path, update_env


_log = logging.getLogger(__name__)


class Software(Extension):

    identifier = 'software'
    label = 'Software Extension'

    def is_available(self, ctx):
        return ctx.project

    def load(self, api):
        api.extend('save_software', api.settings.save_software)
        api.extend('delete_software', api.settings.delete_software)
        api.extend('get_software', self.get_software)
        api.extend('launch', self.launch)
        api.extend('open_with', self.open_with)

    def unload(self, api):
        api.unextend('save_software')
        api.unextend('delete_software')
        api.unextend('get_software')
        api.unextend('launch')
        api.unextend('open_with')

    def get_software(self, api, file=None):
        '''Get the available software.

        If there is a project in the current context only return software in the
        project's "software" list. If a file is provided only return software
        that can handle the file's extension.
        '''

        ext = None
        project_software = None
        available_software = {}

        if file:
            ext = os.path.splitext(file)[-1]

        if api.context.project:
            project_software = api.context.project['software']

        for software_name, software in api.settings['software'].items():
            if ext and ext not in software['extensions']:
                continue
            if project_software and software_name not in project_software:
                continue
            available_software[software_name] = software

        return available_software

    def launch(self, api, name, *args):
        '''Launch the specified software.

        Arguments:
            name (str): Name of software to launch
            *args: Arguments to pass to software executable
        '''

        software = api.settings['software'].get(name, None)
        if not software:
            raise NameError('Could not find software named ' + name)

        found, cmd = _get_command(software)
        if not found:
            raise OSError(
                "Could not find executable for %s. Are you sure it's installed?"
                % name
            )

        args = list(args or software['args'])
        cmd = [cmd] + args
        env = _get_software_env(software, api.context)

        # TODO: run before_launch hooks
        # TODO: create workspace if it does not exist
        _log.debug('Launching %s' % name.title())
        _run(cmd, env=env)

    def open_with(self, api, name, file, *args):
        '''Open a file with the specified software.

        Arguments:
            name (str): Name of software to launch
            file (str): File to open with software
            *args: Arguments to pass to software executable
        '''

        software = api.settings['software'].get(name, None)
        if not software:
            raise NameError('Could not find software named ' + name)

        ext = os.path.splitext(file)[-1]
        if ext not in software['extensions']:
            raise OSError('Can not open %s with %s' % (name, file))

        found, cmd = _get_command(software)
        if not found:
            raise OSError(
                "Could not find executable for %s. Are you sure it's installed?"
                % name
            )

        args = list(args or software['args'])
        cmd = [cmd] + args + [file]
        env = _get_software_env(software, api.context)

        # TODO: run before_launch hooks
        # TODO: create workspace if it does not exist
        _log.debug('Launching %s' % name.title())
        _run(cmd, env=env)


def _get_command(software):
    '''Get the platform specific command used to execute a piece of software.'''

    cmd = software['cmd'][platform]
    if isinstance(cmd, basestring):
        if os.path.isfile(cmd):
            return True, cmd
    for item in cmd:
        if os.path.isfile(item):
            return True, item
    return False, cmd


def _get_software_env(software, ctx):
    '''Get the environment for the specified software.'''

    env = os.environ.copy()
    update_env(env, **ctx.to_envvars())
    update_env(env, **software['env'])
    update_env(
        env,
        CONSTRUCT_HOST=software['host'],
        PYTHONPATH=[get_lib_path()]
    )
    return env


def _run(*args, **kwargs):
    '''On Windows start a detached process in it's own process group.'''

    if platform == 'win':
        create_new_process_group = 0x00000200
        detached_process = 0x00000008
        creation_flags = detached_process | create_new_process_group
        kwargs.setdefault('creationflags', creation_flags)

    kwargs.setdefault('shell', True)
    subprocess.Popen(*args, **kwargs)
