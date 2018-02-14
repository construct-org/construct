# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import fsfs
from construct.action import Action


class Publish(Action):
    label = 'Publish'
    identifier = 'publish'
    description = 'Publish the current file'

    @staticmethod
    def parameters(ctx):
        params = dict(
            task={
                'label': 'Task',
                'required': True,
                'type': fsfs.Entry,
                'help': 'Task',
            },
            version={
                'label': 'Version',
                'required': True,
                'type': int,
                'help': 'File Version'
            }
        )

        if ctx and ctx.task:
            params['task']['default'] = ctx.task

            publishes = list(ctx.task.children('publish'))
            version = 0
            for publish in publishes:
                if publish.name.startswith('v'):
                    pub_version = int(publish.name[1:])
                    if pub_version > version:
                        version = pub_version
            params['version']['default'] = version += 1

        return params

    @staticmethod
    def available(ctx):
        return ctx.task and ctx.host not in ['cli']


class PublishFile(Action):
    label = 'Publish File'
    identifier = 'publish.file'
    description = 'Publish a file to the specified task'


    @staticmethod
    def parameters(ctx):
        params = dict(
            task={
                'label': 'Task',
                'required': True,
                'type': fsfs.Entry,
                'help': 'Task',
            },
            version={
                'label': 'Version',
                'required': True,
                'type': int,
                'help': 'File Version'
            },
            file={
                'label': 'File path',
                'required': True,
                'type': str,
                'help': 'Path to file you want to publish'
            }
        )

        if ctx and ctx.task:
            params['task']['default'] = ctx.task

            publishes = list(ctx.task.children('publish'))
            version = 0
            for publish in publishes:
                if publish.name.startswith('v'):
                    pub_version = int(publish.name[1:])
                    if pub_version > version:
                        version = pub_version
            params['version']['default'] = version += 1

        return params

    @staticmethod
    def available(ctx):
        return ctx.task and ctx.host == 'cli'
