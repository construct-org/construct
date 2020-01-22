# -*- coding: utf-8 -*-

from __future__ import absolute_import

# Standard library imports
from functools import partial
from itertools import zip_longest

# Third party imports
from Qt import QtCore, QtWidgets

# Local imports
from ...context import Context
from ..layouts import VBarLayout
from ..scale import px
from ..state import State
from ..theme import theme
from ..widgets import Frameless, Header, HLine, Navigation


class App(Frameless, QtWidgets.QDialog):

    css_id = ''
    css_properties = {
        'theme': 'surface',
        'border': True,
        'windowTitle': 'Construct Launcher',
        'windowIcon': theme.resources.get('icons/construct.svg'),
    }

    def __init__(self, api, context=None, uri=None, **kwargs):
        super(App, self).__init__(**kwargs)

        # Set App state
        self.state = State(
            api=api,
            context=context or api.get_context(),
            uri=uri,
            bookmarks=api.user_cache.get('bookmarks', []),
        )
        self.state['context'].changed.connect(self.on_ctx_changed)
        self.state['uri'].changed.connect(self.on_uri_changed)

        # Window Attributes
        self.setWindowFlags(
            self.windowFlags() |
            QtCore.Qt.Window
        )
        self.setMinimumSize(*px(600, 700))

        # Create widgets
        self.header = Header('Launcher', parent=self)
        self.header.close_button.clicked.connect(self.hide)

        self.navigation = Navigation(parent=self)
        self.navigation.uri_changed.connect(self.on_uri_changed)
        self.navigation.home_button.clicked.connect(self.on_home_clicked)

        # Layout widgets
        self.layout = VBarLayout(parent=self)
        self.layout.setContentsMargins(*px(1, 1, 1, 1))
        self.layout.setSpacing(0)
        self.layout.top.setSpacing(0)
        self.layout.top.addWidget(self.header)
        self.layout.top.addWidget(self.navigation)
        self.layout.top.addWidget(HLine(parent=self))
        self.setLayout(self.layout)

        # Apply theme
        self.setFocus()
        theme.apply(self)

        # Update UI from initial state
        self._refresh_crumbs(self.state['context'])

    def on_home_clicked(self):
        api = self.state['api'].get()
        context = self._trim_context(api.get_context(), 'location')
        self.state.set('context', context)

        with self.state.signals_blocked():
            self.state.set('uri', '')

    def on_uri_changed(self, uri):
        api = self.state['api'].get()
        context = self._context_from_uri(uri)

        if api.validate_context(context):
            self.state.set('context', context)

    def on_ctx_changed(self, context):
        self._refresh_crumbs(context)

        with self.state.signals_blocked():
            uri = self._uri_from_context(context)
            self.state.set('uri', uri)

    def _context_from_uri(self, uri):
        api = self.state['api'].get()
        uri_parts = uri.strip(' /\\').split('/')
        uri_parts_map = [
            'location',
            'mount',
            'project',
            'bin',
            'asset',
            'workspace',
            'task',
            'file',
        ]
        context = Context(
            host=self.state['context']['host'],
        )
        for key, value in zip_longest(uri_parts_map, parts):
            context[key] = value

        return context

    def _uri_from_context(self, context):
        uri_parts = []
        uri_parts_map = [
            'location',
            'mount',
            'project',
            'bin',
            'asset',
            'workspace',
            'task',
            'file',
        ]
        for key in uri_parts_map:
            value = context.get(key, None)
            if value:
                uri_parts.append(value)
        return '/'.join(uri_parts)

    def _trim_context(self, context, key):
        new_context = Context()
        include = ['location', 'mount', 'project', 'bin', 'asset']
        include = include[:include.index(key)]
        new_context.update(**{k: context[k] for k in include})
        return new_context

    def _build_crumb_menu(self, crumb, key):
        api = self.state['api'].get()
        context = self.state['context'].copy()
        crumb.menu.clear()
        menu_items = []
        if key == 'home':
            locations = api.get_locations()
            for location in locations.keys():
                item_context = Context(
                    host=context['host'],
                    location=location,
                )
                menu_items.append((location, item_context))
        elif key == 'location':
            mounts = api.get_locations()[context['location']]
            for mount in mounts.keys():
                item_context = Context(
                    host=context['host'],
                    location=context['location'],
                    mount=mount,
                )
                menu_items.append((mount, item_context))
        elif key == 'mount':
            with api.set_context(context):
                projects = api.io.get_projects()
            menu_items = []
            for project in projects:
                item_context = Context(
                    host=context['host'],
                    location=context['location'],
                    mount=context['mount'],
                    project=project['name'],
                )
                menu_items.append((project['name'], item_context))
        elif key == 'project':
            with api.set_context(context):
                project = api.io.get_project(
                    context['project'],
                )
            menu_items = []
            for bin in project['bins'].values():
                item_context = Context(
                    host=context['host'],
                    location=context['location'],
                    mount=context['mount'],
                    project=context['project'],
                    bin=bin['name'],
                )
                menu_items.append((bin['name'], item_context))
        elif key == 'bin':
            with api.set_context(context):
                project = api.io.get_project(
                    context['project'],
                )
            menu_items = []
            for asset in project['assets'].values():
                if asset['bin'] != context['bin']:
                    continue
                item_context = Context(
                    host=context['host'],
                    location=context['location'],
                    mount=context['mount'],
                    project=context['project'],
                    bin=asset['bin'],
                    asset=asset['name'],
                )
                menu_items.append((asset['name'], item_context))

        for item_label, item_context in menu_items:
            callback = partial(self.state.set, 'context', item_context)
            crumb.menu.addAction(item_label, callback)

    def _refresh_crumbs(self, context):
        self.navigation.crumbs.clear()

        # Add home arrow
        crumb = self.navigation.crumbs.add('')
        crumb.label.hide()
        crumb_context = self._trim_context(
            self.state['context'].copy(),
            'location',
        )
        crumb.menu.aboutToShow.connect(partial(
            self._build_crumb_menu,
            crumb,
            'home',
        ))

        # Add context crumbs
        for key in ['location', 'mount', 'project', 'bin', 'asset']:
            label = context.get(key, None)
            if label:
                crumb = self.navigation.crumbs.add(label)
                crumb_context = self._trim_context(
                    self.state['context'].copy(),
                    key
                )
                crumb.label.clicked.connect(partial(
                    self.state.set,
                    'context',
                    crumb_context
                ))
                if key == 'asset':
                    crumb.arrow.hide()
                else:
                    crumb.menu.aboutToShow.connect(partial(
                        self._build_crumb_menu,
                        crumb,
                        key,
                    ))
