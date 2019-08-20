# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import absolute_import
import logging

# Third party imports
import fsfs

# Local imports
from . import Migration
from ..compat import Path

_log = logging.getLogger(__name__)


class InitialMigration(object):
    '''Migrates Construct 0.1.x projects.

    Special case - initial migration that needs to be updated until all old
    projects are migrated over.
    '''

    project_tags = set(['project'])
    folder_tags = set(['collection', 'asset_type', 'sequence'])
    asset_tags = set(['asset', 'shot'])
    task_tags = set(['task'])
    workspace_tags = set(['workspace'])

    def __init__(self, api, path):
        self.api = api
        self.path = path

    def forward(self):
        query = fsfs.search(
            root=str(self.path),
            depth=3,
            levels=10,
            skip_root=False
        )
        for entry in query:
            self.migrate(entry)

    def backward(self):
        pass

    def migrate(self, entry):
        tags = set(entry.tags)

        if tags & self.project_tags:
            self.migrate_project(entry)
        elif tags & self.folder_tags:
            self.migrate_folder(entry)
        elif tags & self.asset_tags:
            self.migrate_asset(entry)
        elif tags & self.task_tags:
            self.migrate_task(entry)
        elif tags & self.workspace_tags:
            self.migrate_workspace(entry)
        else:
            print('WARNING: could not migrate %s' % entry)

    def migrate_project(self, project):
        _log.debug('Found project: %s' % project)

        data = project.read()

        data.update(
            name=project.name,
            locations={},
        )

        location_mount = self.api.get_mount_from_path(project.path)
        if location_mount:
            location, mount = location_mount
            data['locations'][location] = mount

        # Fill data with defaults from schema
        data = self.api.schemas.validate('project', data)

        # Update tree
        first_child = project.children().one()
        if first_child:
            folders_path = Path(first_child.path).parent
            try:
                folders = str(folders_path.relative_to(project.path))
            except ValueError:
                folders = ''
        data['tree']['folders'] = folders

        project.tag('project')
        project.uuid = data['_id']
        project.write(**data)

    def migrate_folder(self, folder):
        project = folder.parents().tags('project').one()
        parent = folder.parent()
        _log.debug('Found folder: %s/%s' % (parent.name, folder.name))

        data = folder.read()
        data.update(
            name=folder.name,
            project_id=project.uuid,
            parent_id=parent.uuid,
        )
        data = self.api.schemas.validate('folder', data)

        folder.tag('folder')
        folder.uuid = data['_id']
        folder.write(**data)

    def migrate_asset(self, asset):
        project = asset.parents().tags('project').one()
        parent = asset.parent()
        _log.debug('Found asset: %s/%s' % (parent.name, asset.name))

        if 'shot' in asset.tags:
            asset_type = 'shot'
        else:
            asset_type = 'asset'

        data = asset.read()
        data.update(
            name=asset.name,
            project_id=project.uuid,
            parent_id=parent.uuid,
            asset_type=asset_type,
        )
        data = self.api.schemas.validate('asset', data)

        asset.tag('asset')
        asset.uuid = data['_id']
        asset.write(**data)

    def migrate_task(self, task):
        project = task.parents().tags('project').one()
        parent = task.parent()
        _log.debug('Found task: %s/%s' % (parent.name, task.name))

        data = task.read()
        data.update(
            name=task.name,
            project_id=project.uuid,
            parent_id=parent.uuid,
        )
        data = self.api.schemas.validate('task', data)

        task.tag('task')
        task.uuid = data['_id']
        task.write(**data)

    def migrate_workspace(self, workspace):
        project = workspace.parents().tags('project').one()
        parent = workspace.parent()
        _log.debug('Found workspace: %s/%s' % (parent.name, workspace.name))
