# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

# __all__ = ['init', 'get', 'set', 'get_context', 'get_request', 'search', 'one']

import os
import fsfs
from construct.construct import Construct
from construct.context import _ctx_stack, _req_stack, _cons_stack


def init(*args, **kwargs):
    '''Initialize Construct.

    Create a new Construct instance and make it the active instance. You can
    then retrieve Construct from anywhere using :func:`construct.get`

    Parameters:
        args: Args to pass to Construct
        kwargs: Kwargs to pass to Construct

    Returns:
        Construct instance

    Raises:
        RuntimeError: When Construct.active already exists
    '''

    if Construct.active:
        raise RuntimeError('Construct has already been initialized.')

    inst = Construct(*args, **kwargs)
    Construct.active = inst

    # Setup fsfs entry factory
    from construct.models import factory
    fsfs.set_entry_factory(factory)

    return inst


def get():
    '''Get the active Construct instance'''

    cons = _cons_stack.top or Construct.active
    if not cons:
        raise RuntimeError('Construct has not been initialized.')

    return cons


def set(inst):
    '''Set the active Construct instance

    Parameters:
        inst (Construct): Instance of Construct
    '''

    Construct.active = inst


def set_context(entity):
    Construct.active.set_context_from_path(entity.path)


def get_context():
    '''Get the active Construct instance's context'''

    return _ctx_stack.top or Construct.active.get_context()


def get_request():
    '''Get the active Construct request object'''

    return _req_stack.top


def search(name=None, tags=None, **kwargs):
    '''Search for Construct Entries by name or tag'''

    ctx = get_context()
    root = kwargs.pop('root', None)

    if root is None:
        entry = ctx.get_deepest_entry()
        if entry:
            root = entry.path
        else:
            root = ctx.root or os.getcwd()

    entries = fsfs.search(root, **kwargs)
    if name:
        entries = entries.name(name)
    if tags:
        entries = entries.tags(tags)
    return entries


def one(name=None, tags=None, **kwargs):
    '''Return first result of search'''

    ctx = get_context()
    root = kwargs.pop('root', None)

    if root is None:
        entry = ctx.get_deepest_entry()
        if entry:
            root = entry.path
        else:
            root = ctx.root or os.getcwd()

    entries = fsfs.search(root, **kwargs)
    if name:
        entries = entries.name(name)
    if tags:
        tags = fsfs.util.tupilize(tags)
        entries = entries.tags(*tags)
    return entries.one()


def get_version_path(task, version, ext, workspace, suffix=None):
    cons = Construct.active
    tmpl = cons.get_path_template('version')
    parent = task.parent()
    fields = dict(
        parent=parent,
        task=task,
        version=version,
        workspace=workspace,
        ext=ext
    )

    if suffix:
        fields['suffix'] = suffix

    return tmpl.format(**fields)


# TODO: Expose Construct builtin actions here
# new_project, new_sequence, new_shot, new_asset, new_task, new_workspace

# TODO: Expose Construct methods
# set_context, context_from_path
