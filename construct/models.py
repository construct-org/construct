# -*- coding: utf-8 -*-
from __future__ import absolute_import
import getpass
import datetime
import fsfs
from scandir import scandir
from construct.vendor.lucidity.error import ParseError
from construct.errors import ConfigurationError
from construct.utils import cached_property


factory = fsfs.EntryFactory()


class Entry(factory.Entry):
    '''Base class for all Construct Entry types'''

    default_thumbnail = ''

    def get_comments(self):
        '''Get Entry comments'''

        try:
            return self.read('comments')
        except KeyError:
            return []

    def new_comment(self, body):
        '''Add a new comment to Entry'''

        comment = dict(
            user=getpass.getuser(),
            time=datetime.datetime.utcnow(),
            body=body
        )
        comments = self.get_comments()
        comments.append(comment)
        self.write(comments=comments)

    def get_thumbnail(self):
        '''Get Entry thumbnail'''

        try:
            return self.read_file('thumbnail')
        except KeyError:
            return fsfs.File(self.default_thumbnail, 'rb')

    def set_thumbnail(self, file):
        '''Set Entry thumbnail to file'''

        self.write_file('thumbnail', file)

    def get_status(self):
        '''Get Entry status'''

        try:
            return self.read('status')
        except KeyError:
            self.set_status('waiting')
            return 'waiting'

    def set_status(self, status):
        '''Set status of Entry'''

        from construct import config
        statuses = config['STATUSES'].keys()

        if status not in statuses:
            raise ValueError('Status must be one of: ' + str(statuses))

        self.write(status=status)


factory.Entry = Entry


class Project(Entry):

    @property
    def collections(self):
        return self.children(levels=1).tags('collection')

    @property
    def asset_types(self):
        return self.children(levels=2).tags('asset_type')

    @property
    def assets(self):
        return self.children(levels=3).tags('asset')

    @property
    def sequences(self):
        return self.children(levels=2).tags('sequence')

    @property
    def shots(self):
        return self.children(levels=3).tags('shot')


class Collection(Entry):

    @property
    def sequences(self):
        return self.children(levels=1).tags('sequence')

    @property
    def asset_types(self):
        return self.children(levels=1).tags('asset_type')

    @property
    def assets(self):
        return self.children(levels=2).tags('asset')

    @property
    def shots(self):
        return self.children(levels=2).tags('shot')


class Sequence(Entry):

    @property
    def shots(self):
        return self.children(levels=1).tags('shot')


class Shot(Entry):

    @property
    def tasks(self, *tags):
        return self.children(levels=1).tags('task', *tags)


class AssetType(Entry):

    type_for_tag = 'asset_type'

    @property
    def assets(self):
        return self.children(levels=1).tags('asset')


class Asset(Entry):

    @property
    def tasks(self, *tags):
        return self.children(levels=1).tags('task', *tags)

    @cached_property
    def type(self):
        return self.parent().name


class Task(Entry):

    @cached_property
    def config(self):
        from construct import config
        tasks_cfg = config['TASK_TYPES']
        if self.name in tasks_cfg:
            return tasks_cfg[self.name]
        else:
            for tag in self.tags:
                if tag in tasks_cfg:
                    return tasks_cfg[tag]

    @property
    def short(self):
        return self.config['short']

    @property
    def color(self):
        return self.config['color']

    @property
    def icon(self):
        return self.config['icon']

    @property
    def workspaces(self, *tags):
        return self.children(levels=1).tags('workspace', *tags)

    @property
    def publishes(self, *tags):
        return self.children(levels=1).tags('publish', *tags)

    def get_latest_publish(self):
        publishes = list(self.publishes)
        try:
            return publishes[-1]
        except IndexError:
            pass


class Workspace(Entry):

    @cached_property
    def config(self):
        from construct import config

        software_cfg = config['SOFTWARE']
        for app_name, app_cfg in software_cfg.items():
            if app_cfg['host'] == self.name:
                return app_cfg
            else:
                for tag in self.tags:
                    if app_cfg['host'] == tag:
                        return app_cfg

    @property
    def icon(self):
        return self.config['icon']

    def get_work_files(self):
        import construct
        path_template = construct.get_path_template('workspace_file')
        versions = {}
        for f in scandir(self.path):
            try:
                data = path_template.parse(f.name)
                data['version'] = int(data['version'])
                file_type = construct.get_file_type(f.name)
                if file_type:
                    file_type = file_type[0]
                else:
                    file_type = scene_data['ext'][1:]
                data['file_type'] = file_type
            except ParseError:
                continue
            versions[f.name] = data
        return versions

    def get_latest_version(self, name, ext):
        '''Get the latest version of a workfile.

        Arguments:
            name (str): The name of the version to lookup
            ext (str): The extension of the workfile
        Returns:
            version dict
        '''
        task = self.parent().short
        versions = self.get_work_files()
        version = 0
        latest_version = None

        for data in versions.values():
            is_match = (
                data['name'] == name and
                data['task'] == task and
                data['ext'] == ext
            )
            if is_match and data['version'] > version:
                latest_version = data

        return latest_version

    def get_next_version(self, name, ext):
        '''Get the next version number of a workfile.

        Arguments:
            name (str): The name of the version to lookup
            ext (str): The extension of the workfile
        Returns:
            int
        '''
        task = self.parent().short
        versions = self.get_work_files()
        version = 0

        for data in versions.values():
            is_match = (
                data['name'] == name and
                data['task'] == task and
                data['ext'] == ext
            )
            if is_match:
                version = max(version, data['version'])

        return version + 1

    def new_version(self, user, name, version, file_type, file):
        import os
        relative_path = os.path.relpath(file, self.path)
        version = Version(
            user=user,
            file_type=file_type,
            file=relative_path,
            name=name,
            version=version,
        )
        data = self.read()
        data.setdefault('versions', [])
        data['versions'].append(version)
        self.write(**data)


class EmbeddedModel(dict):

    __fields__ = []

    def __init__(self, *args, **kwargs):
        super(Version, self).__init__(*args, **kwargs)
        self.__dict__ = self
        for field in self.__fields__:
            if field not in self:
                raise ValueError('Missing keyword argument: %s' % field)


class Version(EmbeddedModel):

    __field__ = ['user', 'name', 'version', 'file_type', 'file']


def is_entry(obj):
    '''Returns True if obj is an instance of Entry or EntryProxy'''
    return isinstance(obj, (factory.Entry, factory.EntryProxy))
