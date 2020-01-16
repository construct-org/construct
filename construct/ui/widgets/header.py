# -*- coding: utf-8 -*-

# Third party imports
from Qt import QtCore, QtWidgets

# Local imports
from ..layouts import HBarLayout
from ..scale import px
from . import H2, Glyph, IconButton, Widget


__all__ = [
    'Header',
]


class Header(Widget, QtWidgets.QWidget):

    css_id = 'background'
    css_properties = {
        'theme': 'background',
    }

    def __init__(self, label, *args, **kwargs):
        super(Header, self).__init__(*args, **kwargs)

        for prop, value in self.css_properties.items():
            self.setProperty(prop, value)

        self.glyph = Glyph('construct')
        self.title = H3(label)
        self.title.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.close_button = IconButton(icon='close')

        self.layout = HBarLayout()
        self.layout.left.addWidget(self.glyph, stretch=1)
        self.layout.center.addWidget(self.title)
        self.layout.right.addWidget(self.close_button)
        self.setLayout(self.layout)
