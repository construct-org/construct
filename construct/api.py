# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import fsfs
import logging
from logging.config import dictConfig
from itertools import chain
import yaml
from construct.vendor import lucidity
from construct.context import _ctx_stack, _req_stack, Context
from construct.config import Config
from construct.extension import ExtensionCollector, Extension, HostExtension
from construct.action import Action, ActionCollector, ActionProxy
from construct.constants import DEFAULT_LOGGING
from construct.actioncontext import ActionContext
from construct.utils import unipath, ensure_instance
from construct.stats import log_call
from construct.errors import TemplateError

__all__ = [
    'Context',
    'config',
    'Config',
    'config_file',
    'extensions',
    'Extension',
    'HostExtension',
    'actions',
    'Action',
    'ActionContext',
    'ActionProxy',
    'init',
    'uninit',
    'set_context',
    'set_context_from_entry',
    'set_context_from_path',
    'get_context',
    'get_request',
    'search',
    'quick_select',
    'get_path_template',
    'get_path_templates',
    'get_template_search_paths',
    'get_templates',
    'get_template',
    'get_host',
    'get_form',
    'get_form_cls',
    'show_form',
    'new_project',
    'new_sequence',
    'new_shot',
    'new_asset',
    'new_task',
    'new_workspace',
    'new_template',
    'publish',
    'publish_file',
    'save',
]


logging.config.dictConfig(DEFAULT_LOGGING)
_log = logging.getLogger(__name__)
_initialized = False
_context = None
config = Config()
config_file = None
extensions = ExtensionCollector()
actions = ActionCollector(extensions)


@log_call
def init(root=None, host=None, extension_paths=None, logging=None):
    '''Initialize Construct'''

    global _initialized
    if _initialized:
        raise RuntimeError('Construct has already been initialized.')

    # Load configuration
    global config_file
    config_file = os.environ.get('CONSTRUCT_CONFIG')
    if config_file:
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f.read())
        config.update(config_data)

    # Configure logging
    dictConfig(logging or config.get('LOGGING', DEFAULT_LOGGING))

    if config_file:
        _log.debug('Loaded config: %s' % config_file)
    else:
        _log.debug('Using default config')

    # Setup fsfs entry factory
    _log.debug('Configuring fsfs...')
    from construct.models import factory
    from construct.constants import FSFS_DATA_ROOT, FSFS_DATA_FILE
    fsfs.set_entry_factory(factory)
    fsfs.set_data_root(FSFS_DATA_ROOT)
    fsfs.set_data_file(FSFS_DATA_FILE)

    # Setup initial context
    global _context
    _log.debug('Setting initial context...')
    _context = Context.from_env()
    if root:
        _log.debug('Setting root to %s' % root)
        _context.root = unipath(root)
    elif 'CONSTRUCT_ROOT' in os.environ:
        _log.debug('Setting root to %s' % os.environ['CONSTRUCT_ROOT'])
        _context.root = unipath(os.environ['CONSTRUCT_ROOT'])
    else:
        _log.debug('Setting root to %s' % config['ROOT'])
        _context.root = unipath(config['ROOT'])

    if host:
        _context.host = host

    # Discover extensions
    _log.debug('Discovering extensions...')
    extension_paths = extension_paths or []
    extensions.discover(*extension_paths)

    # Register builtins
    from construct.builtins import Builtins
    extensions.register(Builtins)

    _log.debug('Initialized!')
    _initialized = True


@log_call
def uninit():
    '''Uninitialize Construct...'''

    global _initialized
    if not _initialized:
        raise RuntimeError('Construct has not been initialized yet...')

    global config
    _log.debug('Setting default config...')
    config = Config()

    global config_file
    config_file = None

    global _context
    _log.debug('Clearing context...')
    _context = None

    _log.debug('Removing all extensions...')
    extensions.clear()

    _log.debug('Restoring default fsfs policy...')
    fsfs.set_default_policy()

    _log.debug('Uninitialized!')
    _initialized = False


@log_call
def set_context(ctx):
    '''Manually set the current context to the specified :class:`Context`'''
    ensure_instance(ctx, Context)

    global _context
    _context = ctx


@log_call
def set_context_from_entry(entry):
    '''Extract and set the current context from the specified entry'''

    global _context
    new_context = Context.from_path(entry.path)
    _context.update(new_context, exclude=['host', 'root'])


@log_call
def set_context_from_path(path):
    '''Extract and set the current context from the specified path'''

    global _context
    new_context = Context.from_path(path)
    _context.update(new_context, exclude=['host', 'root'])


@log_call
def get_context():
    '''Get current :class:`Context`'''

    return _ctx_stack.top or _context


@log_call
def get_request():
    '''Get current task :class:`Request`'''

    return _req_stack.top


@log_call
def get_host(name=None):
    '''Get current host extension or get host by name'''

    ctx = get_context()
    host = name or ctx.host
    return extensions.get(host, None)


@log_call
def get_form_cls(action_identifier):
    '''Get form for action_identifier'''

    for ext in extensions:
        form = ext.get_form(action_identifier)
        if form:
            return form


@log_call
def get_form(action_identifier, action=None, ctx=None, parent=None):
    '''Return a form instance for an action_identifier.'''

    from construct_ui import resources
    resources.init()

    action = action or actions.get(action_identifier)
    parent = parent or get_host().get_qt_parent()
    ctx = ctx or get_context()

    form_cls = get_form_cls(action_identifier)
    if not form_cls:
        return

    form = form_cls(action, ctx, parent)
    form.setStyleSheet(resources.style(config['STYLE']))
    return form


@log_call
def show_form(action_identifier, action=None, ctx=None, parent=None):
    '''Show and return a form instance for an action_identifier.'''

    form = get_form(action_identifier, action, ctx, parent)

    if not form:
        # TODO: replace with construct error
        raise RuntimeError('Form does not exist for %s' % action_identifier)

    form.show()
    return form


@log_call
def get_path_template(name):
    '''Get one of the current projects templates by name'''

    return lucidity.Template(name, config['PATH_TEMPLATES'][name], anchor=None)


@log_call
def get_path_templates():
    '''Get a dict containining the current projects templates'''

    return {k: lucidity.Template(k, v, anchor=None)
            for k, v in config['PATH_TEMPLATES']}


@log_call
def get_template_search_paths():

    ctx = get_context()

    paths = set()
    if ctx.project:
        paths.add(unipath(ctx.project.data.path, 'templates'))

    for ext in extensions:
        paths.update(ext._template_paths)

    return [p for p in paths if os.path.isdir(p)]


@log_call
def get_template(name, *tags):
    '''Get a template by tag and name'''

    templates = get_templates(*tags)

    alt = None
    for template in templates.values():
        if name == template.name:
            return template
        if name in template.name:
            alt = template.name

    if alt:
        msg = '"{}" not found, did you mean "{}"?'.format(name, alt)
    else:
        msg = '"{}" not found'.format(name)
    raise TemplateError(msg)


@log_call
def get_templates(*tags):
    '''Get all templates matching a set of tags.'''

    entries = chain(*(
        fsfs.search(path, depth=1).tags(*tags)
        for path in get_template_search_paths()
    ))

    templates = {}
    for template in entries:
        if template.name in templates:
            continue
        templates[template.name] = template

    return templates


@log_call
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
        tags = fsfs.util.tupilize(tags)
        entries = entries.tags(*tags)
    return entries


@log_call
def quick_select(selector, **kwargs):
    '''Quickly find one Entry using a selector string like entry1/entry2'''

    ctx = get_context()
    root = kwargs.pop('root', None)

    if root is None:
        entry = ctx.get_deepest_entry()
        if entry:
            root = entry.path
        else:
            root = ctx.root or os.getcwd()

    first_depth = 5 if ctx.project else 3
    if ctx.project:
        first_depth = 4

    return fsfs.quick_select(root, selector, first_depth=first_depth)


# Builtin Action Aliases

new_project = ActionProxy('new.project')
new_sequence = ActionProxy('new.sequence')
new_shot = ActionProxy('new.shot')
new_asset_type = ActionProxy('new.asset_type')
new_asset = ActionProxy('new.asset')
new_task = ActionProxy('new.task')
new_workspace = ActionProxy('new.workspace')
new_template = ActionProxy('new.template')
save = ActionProxy('save')
publish = ActionProxy('publish')
publish_file = ActionProxy('publish_file')
