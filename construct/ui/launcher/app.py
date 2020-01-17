# -*- coding: utf-8 -*-

from __future__ import absolute_import

# Third party imports
from Qt import QtCore, QtWidgets

# Local imports
from ..layouts import VBarLayout
from ..scale import px
from ..theme import theme
from ..widgets import Frameless, Header, Navigation, HLine


class App(Frameless, QtWidgets.QDialog):

    css_id = ''
    css_properties = {
        'theme': 'surface',
        'border': True,
        'windowTitle': 'Construct Launcher',
        'windowIcon': theme.resources.get('icons/construct.svg'),
    }

    def __init__(self, api, uri=None, **kwargs):
        super(App, self).__init__(**kwargs)

        # Set App attributes
        self.api = api
        self.uri = uri

        # Window Attributes
        self.setWindowFlags(
            self.windowFlags() |
            QtCore.Qt.Window
        )
        self.setMinimumWidth(600)
        self.setMinimumHeight(700)

        # Create widgets
        self.header = Header('Launcher', parent=self)
        self.header.close_button.clicked.connect(self.hide)

        self.navigation = Navigation(parent=self)

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
