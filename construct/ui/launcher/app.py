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
        'border': True
    }

    def __init__(self, uri=None, **kwargs):
        super(App, self).__init__(**kwargs)

        self.uri = uri

        self.setWindowFlags(
            QtCore.Qt.Dialog |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint
        )

        self.header = Header('Launcher', parent=self)
        self.header.close_button.clicked.connect(self.accept)

        self.navigation = Navigation(parent=self)

        self.layout = VBarLayout()
        self.layout.setContentsMargins(*px(1, 1, 1, 1))
        self.layout.setSpacing(0)
        self.layout.top.setSpacing(0)
        self.layout.top.addWidget(self.header)
        self.layout.top.addWidget(self.navigation)
        self.layout.top.addWidget(HLine(parent=self))
        self.setLayout(self.layout)

        theme.apply(self)

        # Focus on the dialog itself
        self.setFocus()

        self.setMinimumWidth(600)
        self.setMinimumHeight(700)
