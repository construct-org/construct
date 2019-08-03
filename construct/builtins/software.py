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
from ..utils import get_lib_path, update_env, update_dict


_log = logging.getLogger(__name__)


class Software(Extension):

    identifier = 'software'
    label = 'Software Extension'

    def is_available(self, ctx):
        return ctx.project

    def load(self, api):
        api.settings.add_section('software', 'software')
        api.extend('save_software', self.save)
        api.extend('delete_software', self.delete)
        api.extend('get_software', self.get)
        api.extend('get_software_by_name', self.get_by_name)
        api.extend('update_software', self.update)
        api.extend('launch', self.launch)
        api.extend('open_with', self.open_with)

    def unload(self, api):
        api.unextend('save_software')
        api.unextend('delete_software')
        api.unextend('get_software')
        api.unextend('get_software_by_name')
        api.unextend('update_software')
        api.unextend('launch')
        api.unextend('open_with')

    @property
    def software(self):
        return self.api.settings['software']

    def _get_project_software(self, api, project):
        project = api.io.get_project_by_id(project['_id'])
        return project.get('software', {})

    def update(self, api, name, data, project=None):
        '''Update software stored in settings or a project.'''

        if project:
            # Get updated project software
            software = self._get_project_software(api, project)
            software_data = software.get(name, {})

            # Update software data
            update_dict(software_data, data)

            # Validate software data
            software_data = self.software.validate(software_data)
            software[name] = software_data

            # Update project with software
            api.io.update_project(project, {'software': software})
            return software[name]

        software_data = self.software.get(name, {})
        update_dict(software_data, data)
        self.software.write(name, software_data)
        return software_data

    def save(self, api, name, data, project=None):
        '''Save software to settings or a project.'''

        if project:
            software = self._get_project_software(api, project)
            software[name] = self.software.validate(data)
            api.io.update_project(project, {'software': software})
            return software[name]

        return self.software.write(name, data)

    def delete(self, api, name, project=None):
        '''Delete software by name from settings or a project.'''

        if project:
            software = self._get_project_software(api, project)
            if name not in software:
                return
            software.pop(name)
            api.io.update_project(project, {'software': software})

        self.software.delete(name)

    def get_by_name(self, api, name, project=None, file=None):
        try:
            return self.get(api, project, file)[name]
        except KeyError:
            raise NameError('Could not find software named ' + name)

    def _available_software(self, software, ext=None):
        available = {}
        for software_name, software in software.items():
            if ext and ext not in software['extensions']:
                continue
            available[software_name] = software
        return available

    def get(self, api, project=None, file=None):
        '''Get the available software.

        If a project is provided get only software available in that project.

        If there is a project in the current context only return software in the
        project's "software" dict. If a file is provided only return software
        that can handle the file's extension.

        If a file is provided, only return software that can open that file.
        '''

        ext = None
        project = project or api.context.project

        if file:
            ext = os.path.splitext(file)[-1]

        if project:
            software = self._get_project_software(api, project)
            return self._available_software(software, ext)

        return self._available_software(self.software, ext)

    def launch(self, api, name, *args, **kwargs):
        '''Launch the specified software.

        Arguments:
            name (str): Name of software to launch
            args: Arguments to pass to software executable
            context: Context to launch software in
        '''

        software = self.get_by_name(api, name)

        found, cmd = _get_command(software)
        if not found:
            raise OSError(
                "Could not find executable for %s."
                % name
            )

        ctx = kwargs.pop('context', api.context).copy()
        args = list(args or software['args'])
        cmd = [cmd] + args
        env = _get_software_env(software, ctx, api.path)

        # TODO: run before_launch hooks
        # TODO: create workspace if it does not exist
        _log.debug('Launching %s' % name.title())
        _run(cmd, env=env)

    def open_with(self, api, name, file, *args, **kwargs):
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

        ctx = kwargs.pop('context', api.context).copy()
        ctx.file = file
        args = list(args or software['args'])
        cmd = [cmd] + args + [file]
        env = _get_software_env(software, ctx, api.path)

        # TODO: run before_launch hooks
        # TODO: create workspace if it does not exist
        _log.debug('Launching %s' % name.title())
        _run(cmd, env=env)


def _get_command(software):
    '''Get the platform specific command used to execute a piece of software.'''

    cmd = software['cmd'].get(platform, None)
    if isinstance(cmd, basestring):
        if os.path.isfile(cmd):
            return True, cmd
    for item in cmd:
        if os.path.isfile(item):
            return True, item
    return False, cmd


def _get_software_env(software, ctx, path):
    '''Get the environment for the specified software.'''

    env = os.environ.copy()
    update_env(env, **ctx.to_envvars())
    update_env(env, **software['env'])
    update_env(
        env,
        CONSTRUCT_PATH=os.pathsep.join([str(p) for p in path]),
        CONSTRUCT_HOST=software['host'],
        PYTHONPATH=[get_lib_path().as_posix()]
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
