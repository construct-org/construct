# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
from construct import api
from construct.action import Action
from construct.tasks import (
    task,
    pass_context,
)
from construct.utils import platform
import subprocess
import shlex



class Edit(Action):
    '''Open current location in text editor.'''

    label = 'Edit Model'
    identifier = 'edit'

    @staticmethod
    def available(ctx):
        return (
            ctx.host == 'cli' and
            ctx.project
        )


@task
@pass_context
def edit(ctx):
    '''Edit the current entry.'''
    editor = os.environ.get('EDITOR', 'subl --wait')
    path = os.path.abspath(ctx.get_deepest_entry().data.path)
    cmd = shlex.split(editor) + [path]

    kwargs = {
        'stdout': subprocess.PIPE,
        'stderr': subprocess.STDOUT,
    }
    if platform == 'win':
        CREATE_NO_WINDOW = 0x08000000
        kwargs['creationflags'] = CREATE_NO_WINDOW

    subprocess.Popen(cmd, **kwargs)
