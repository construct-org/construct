# -*- coding: utf-8 -*-
from __future__ import absolute_import
from .fsfs import FsfsLayer
from .mongo import MongoLayer
from ..errors import ValidationError


class IO(object):

    def __init__(self, api):
        self.api = api
        self.settings = self.api.settings
        self.fsfs = FsfsLayer(api)

    def load(self):
        self.api.define(
            'before_new_project',
            '(api, project): Sent before a project is created.'
        )
        self.api.define(
            'after_new_project',
            '(api, project): Sent after a project is created.'
        )
        self.api.define(
            'before_update_project',
            '(api, project, update): Sent before a project is updated.'
        )
        self.api.define(
            'after_update_project',
            '(api, project): Set after a project is updated.'
        )

    def unload(self):
        self.api.undefine('before_new_project')
        self.api.undefine('after_new_project')
        self.api.undefine('before_update_project')
        self.api.undefine('after_update_project')

    def get_projects(self, location=None, mount=None):
        '''Get a list of projects in a location and mount. If no mount is
        provided list projects in all mounts of the given location.

        .. note:: Locations and mounts are configured in your construct.yaml

        Arguments:
            location (str): Location of projects. Default: my_location setting
            mount (str): Mount project resides in. Optional.

        Returns:
            Generator or cursor yielding projects
        '''

        location = location or self.settings['my_location']
        return self.fsfs.get_projects(location, mount)

    def get_project(self, name, location=None, mount=None):
        '''Get one project that matches the given name. You can specify a
        location and mount to narrow the search.

        .. note:: Locations and mounts are configured in your construct.yaml

        Arguments:
            name (str): Partial name of project.
            location (str): Location of projects. Default: my_location setting
            mount (str): Mount project resides in. Optional.

        Returns:
            Project dict or None
        '''

        location = location or self.settings['my_location']
        return self.fsfs.get_project(name, location, mount)

    def new_project(self, name, location, mount, data=None):
        '''Create a new project in the specified location and mount.

        .. note:: Locations and mounts are configured in your construct.yaml

        Events:
            before_new_project: Sent with api and project data
            after_new_project: Sent with api and result project data

        Arguments:
            name (str): Full name of new project.
            location (str): Location of new project.
            mount (str): Mount within the specified location.

        Returns:
            New Project dict.
        '''

        # Prepare data
        data = data or {}
        data.setdefault('name', name)
        data.setdefault('locations', {location: mount})

        self.api.send('before_new_project', self.api, data)

        # Validate data
        v = self.api.schemas.get_validator('project')
        data = v.validated(data)
        if not data:
            raise ValidationError(
                'Invalid project data: %s' % v.errors,
                errors=v.errors
            )

        # Create our new project
        result = self.fsfs.new_project(name, location, mount, data)

        self.api.send('after_new_project', self.api, result)
        return result

    def update_project(self, project, data):
        '''Update a project's data.

        Events:
            before_update_project: Sent with api, project, and update
            after_update_project: Sent with api, updated project

        Arguments:
            project (dict): Project data containing at least a name
            data (dict): Data to update

        Returns:
            Updated project data.
        '''

        self.api.send('before_update_project', self.api, project, data)

        #Validate data
        v = self.api.schemas.get_validator('project')
        data = v.validated(data, update=True)
        if not data:
            raise ValidationError(
                'Invalid project data: %s' % v.errors,
                errors=v.errors
            )

        # Update our project
        result = self.fsfs.update_project(project, data)
        self.api.send('after_update_project', self.api, result)
        return result

    def delete_project(self, project):
        '''Delete a project.

        .. warning:: This does not delete your project data on the file system.
        It simply removes metadata. You are in charge of delete files on your
        file system.
        '''

        return self.fsfs.delete_project(project)
