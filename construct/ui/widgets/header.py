# -*- coding: utf-8 -*-

# Third party imports
from Qt import QtWidgets

# Local imports
from . import Widget
from ..layouts import HBarLayout


class Header(Widget, QtWidgets.QWidget):

    css_id = 'header'
    css_properties = {
        'theme': 'background',
    }

    def __init__(self, label, icon, close_icon, parent=None):
        super(Header, self).__init__(parent=parent)

        self.setObjectName(self.css_id)
        for prop, value in self.css_properties.items():
            self.setProperty(prop, value)

        layout = HBarLayout()
        self.setLayout(layout)
