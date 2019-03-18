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

    def _get_projects(self, location, mount=None):
        if mount:
            root = self.api.get_mount(location, mount).as_posix()
            for entry in fsfs.search(root, levels=1).tags('project'):
                yield entry

        for mount in self.settings['locations'][location].keys():
            root = self.api.get_mount(location, mount).as_posix()
            results = fsfs.search(root, levels=1).tags('project')
            for entry in results:
                yield entry

    def get_projects(self, location, mount=None):
        for entry in self._get_projects(location, mount):
            yield entry.read()

    def get_project_by_id(self, _id, location=None, mount=None):

        first_location = location or self.settings['my_location']
        locations = sorted(
            self.settings['locations'].keys(),
            key=lambda location: int(location == first_location),
            reverse=True
        )
        for location in locations:
            for project in self._get_projects(location):
                if project.uuid == _id:
                    return project.read()

    def get_project(self, name, location, mount=None):
        if mount:
            root = self.api.get_mount(location, mount).as_posix()
            entry = fsfs.search(root, levels=1).name(name).one()
            if entry:
                return entry.read()
            return

        for mount in self.settings['locations'][location].keys():
            root = self.api.get_mount(location, mount).as_posix()
            entry = fsfs.search(root, levels=1).name(name).one()
            if entry:
                return entry.read()

    def new_project(self, name, location, mount, data):
        path = self.api.get_mount(location, mount) / name
        entry = fsfs.get_entry(path.as_posix())

        if entry.exists:
            raise OSError('Project already exists.')

        entry.tag('project')
        entry.write(**data)
        entry.uuid = data['_id']
        return entry.read()

    def update_project(self, project, data):
        path = self.api.get_path_to(project)
        entry = fsfs.get_entry(path.as_posix())

        if not entry.exists:
            raise OSError('Project does not exist.')

        entry.write(**data)
        return entry.read()

    def delete_project(self, project):
        path = self.api.get_path_to(project)
        entry = fsfs.get_entry(path.as_posix())
        entry.delete()

    def _get_parent(self, entity):
        if entity['_type'] == 'project':
            return

        if 'project_id' in entity:
            project = self.get_project_by_id(entity['project_id'])
            project_path = self.api.get_path_to(project)
            if entity['parent_id'] == entity['project_id']:
                return fsfs.get_entry(project_path.as_posix())

            matches = (
                project_path / project['tree']['folders']
            ).rglob('uuid_' + entity['parent_id'])
            if not matches:
                raise OSError('Could not find parent of %s' % entity['name'])

            entry_path = matches[0].parent.parent
            entry = fsfs.get_entry(entry_path.as_posix())
            return entry

    def get_folders(self, parent):
        parent_path = self.api.get_path_to(parent)
        if parent['_type'] == 'project':
            parent_path = parent_path / parent['tree']['folders']
        entries = fsfs.search(parent_path, levels=1, skip_root=True)
        for entry in entries:
            if set(entry.tags).intersection(set(self._folder_tags)):
                yield entry.read()

    def get_folder(self, name, parent):
        prospect = None
        for folder in self.get_folders(parent):
            if name in folder['name']:
                prospect = folder
            elif name == folder['name']:
                return folder
        return prospect

    def new_folder(self, name, parent, data):
        parent_path = self.api.get_path_to(parent)
        if parent['_type'] == 'project':
            parent_path = parent_path / parent['tree']['folders']
        folder_path = parent_path / name

        entry = fsfs.get_entry(folder_path.as_posix())
        entry.tag('folder')
        entry.write(**data)
        entry.uuid = data['_id']
        return entry.read()

    def update_folder(self, folder, data):
        path = self.api.get_path_to(folder)
        entry = fsfs.get_entry(path.as_posix())

        if not entry.exists:
            raise OSError('Folder does not exist.')

        entry.write(**data)
        return entry.read()

    def delete_folder(self, folder):
        path = self.api.get_path_to(folder)
        entry = fsfs.get_entry(path.as_posix())
        entry.delete()

    def get_assets(self, parent):
        return NotImplemented

    def get_asset(self, name, parent):
        return NotImplemented

    def new_asset(self, name, parent, data):
        return NotImplemented

    def update_asset(self, asset, data):
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

    def new_workfile(self, asset, name, identifier, task, file_type, data):
        return NotImplemented

    def new_publish(self, asset, name, identifier, task, file_type, data):
        return NotImplemented
