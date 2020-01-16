# -*- coding: utf-8 -*-

from __future__ import absolute_import

# Third party imports
from Qt import QtCore, QtWidgets

# Local imports
from ..layouts import VBarLayout
from ..theme import theme
from ..widgets import Frameless, Header


class App(Frameless, QtWidgets.QDialog):

    css_id = 'surface'

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

        self.layout = VBarLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.top.addWidget(self.header)
        self.setLayout(self.layout)

        theme.apply(self)
