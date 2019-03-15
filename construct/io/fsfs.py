# -*- coding: utf-8 -*-
from __future__ import absolute_import
import fsfs


class FsfsLayer(object):

    # This maintains backwards compatability with construct 0.1.0
    # These tags should all be converted to folder when we make the switch
    _folder_tags = ['folder', 'collection', 'sequence', 'asset_type']

    def __init__(self, api):
        self.api = api
        self.settings = api.settings

    def get_projects(self, location, mount=None):
        if mount:
            root = self.api.get_mount(location, mount)
            for entry in fsfs.search(root, levels=1).tags('project'):
                yield entry.read()

        for mount in self.settings['locations'][location].keys():
            root = self.api.get_mount(location, mount)
            results = fsfs.search(root, levels=1).tags('project')
            for entry in results:
                yield entry.read()

    def get_project_by_id(self, _id, location=None, mount=None):

        first_location = location or self.settings['my_location']
        locations = sorted(
            self.settings['locations'].keys(),
            key=lambda location: int(location == first_location),
            reverse=True
        )
        for location in locations:
            for project in self.get_projects(location):
                if project['_id'] == _id:
                    return project

    def get_project(self, name, location, mount=None):
        if mount:
            root = self.api.get_mount(location, mount)
            entry = fsfs.search(root, levels=1).name(name).one()
            if entry:
                return entry.read()
            return

        for mount in self.settings['locations'][location].keys():
            root = self.api.get_mount(location, mount)
            entry = fsfs.search(root, levels=1).name(name).one()
            if entry:
                return entry.read()

    def new_project(self, name, location, mount, data):
        path = self.api.get_mount(location, mount) + '/' + name
        entry = fsfs.get_entry(path)

        if entry.exists:
            raise OSError('Project already exists.')

        entry.tag('project')
        entry.write(**data)
        return entry.read()

    def update_project(self, project, data):
        path = self.api.get_path_to(project)
        entry = fsfs.get_entry(path)

        if not entry.exists:
            raise OSError('Project does not exist.')

        entry.write(**data)
        return entry.read()

    def delete_project(self, project):
        path = self.api.get_path_to(project)
        model = fsfs.get_entry(path)
        model.delete()

    def get_folders(self, parent):
        return NotImplemented

    def get_folder(self, name, parent):
        return NotImplemented

    def new_folder(self, name, parent, **data):
        return NotImplemented

    def update_folder(self, group, **data):
        return NotImplemented

    def delete_folder(self, group):
        return NotImplemented

    def get_assets(self, parent):
        return NotImplemented

    def get_asset(self, name, parent):
        return NotImplemented

    def new_asset(self, name, parent, **data):
        return NotImplemented

    def update_asset(self, asset, **data):
        return NotImplemented

    def delete_asset(self, asset):
        return NotImplemented

    def get_tasks(self, asset):
        return NotImplemented

    def get_task(self, name, asset):
        return NotImplemented

    def new_task(self, name, asset):
        return NotImplemented

    def delete_task(self, task):
        return NotImplemented

    def get_workfiles(self, asset):
        return NotImplemented

    def get_publishes(self, asset):
        return NotImplemented

    def get_latest_workfile(self, asset, name, task, file_type):
        return NotImplemented

    def get_latest_publish(self, asset, name, task, file_type, instance=0):
        return NotImplemented

    def get_next_workfile(self, asset, name, task, file_type):
        return NotImplemented

    def get_next_publish(self, asset, name, task, file_type, instance=0):
        return NotImplemented

    def new_workfile(self, asset, name, identifier, task, file_type, **data):
        return NotImplemented

    def new_publish(self, asset, name, identifier, task, file_type, **data):
        return NotImplemented
