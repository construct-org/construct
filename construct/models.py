# -*- coding: utf-8 -*-
from __future__ import absolute_import
import getpass
import datetime
import fsfs
from scandir import scandir
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
    def asset_types(self):
        return self.children('asset_type')

    @property
    def assets(self):
        return self.children('asset')

    @property
    def sequences(self):
        return self.children('sequence')

    @property
    def shots(self):
        return self.children('shot')


class Sequence(Entry):

    @property
    def shots(self):
        return self.children('shot')


class Shot(Entry):

    @property
    def tasks(self, *tags):
        return self.children('task', *tags)


class AssetType(Entry):

    type_for_tag = 'asset_type'

    @property
    def assets(self):
        return self.children('asset')


class Asset(Entry):

    @property
    def tasks(self, *tags):
        return self.children('task', *tags)

    @cached_property
    def type(self):
        return self.parent('asset_type').name


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
        return self.children('workspace', *tags)

    @property
    def publishes(self, *tags):
        return self.children('publish', *tags)

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
        for app_name, app_cfg in config['SOFTWARE'].items():
            if app_cfg['host'] == self.name:
                return app_cfg
            else:
                for tag in self.tags:
                    if app_cfg['host'] == tag:
                        return app_cfg

    @property
    def icon(self):
        return self.config['icon']

    @property
    def versions(self):
        import construct
        path_template = construct.get_path_template('workspace_file')
        versions = []
        for f in scandir(self.path):
            try:
                data = path_template.parse(f)
            except:
                continue
            versions.append(data)
        return versions

    def get_next_version(self, name, ext):
        task = self.parent('task')
        versions = []

    def get_latest_version(self):
        pass

    def new_version(self, user, name, version, file_type, file):
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
