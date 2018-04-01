# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division
import getpass
import datetime
import fsfs
from construct.errors import ConfigurationError


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
            pass

        try:
            if 'project' in self.tags:
                statuses = self.read('statuses')
            else:
                project = self.parent('project')
                statuses = project.read('statuses')
        except KeyError:
            raise ConfigurationError(
                'Project missing key "statuses"'
            )

        return statuses[0]

    def set_status(self, status):
        '''Set status of Entry'''

        if 'project' in self.tags:
            statuses = self.read('statuses')
        else:
            project = self.parent('project')
            statuses = project.read('statuses')
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


class Asset(Entry):

    @property
    def tasks(self, *tags):
        return self.children('task', *tags)


class Task(Entry):

    @property
    def workspaces(self, *tags):
        return self.children('workspaces', *tags)

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

    @property
    def versions(self):
        pass

    def get_latest_version(self):
        pass

    @property
    def publishes(self):
        pass

    def get_latest_publish(self):
        pass


def is_entry(obj):
    '''Returns True if obj is an instance of Entry or EntryProxy'''
    return isinstance(obj, (factory.Entry, factory.EntryProxy))
