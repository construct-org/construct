# -*- coding: utf-8 -*-

class IOLayer(object):

    def get_projects(self, location, mount=None):
        return NotImplemented

    def get_project_by_id(self, _id, location=None, mount=None):
        return NotImplemented

    def get_project(self, name, location, mount=None):
        return NotImplemented

    def new_project(self, name, location, mount, data):
        return NotImplemented

    def update_project(self, project, data):
        return NotImplemented

    def delete_project(self, project):
        return NotImplemented

    def get_assets(self, project, bin=None, asset_type=None, group=None):
        return NotImplemented

    def get_asset(self, project, name):
        return NotImplemented

    def new_asset(self, project, data):
        return NotImplemented

    def update_asset(self, asset, data):
        return NotImplemented

    def delete_asset(self, asset):
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

    def get_path_to(self, entity):
        return NotImplemented
