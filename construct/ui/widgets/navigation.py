# -*- coding: utf-8 -*-

# Third party imports
from Qt import QtCore, QtWidgets

# Local imports
from ..layouts import HBarLayout
from ..scale import px
from . import P, H2, Glyph, Button, IconButton, Widget


__all__ = [
    'Navigation',
]


class Navigation(Widget, QtWidgets.QWidget):

    css_id = 'navigation'
    css_properties = {
        'theme': 'surface',
    }

    def __init__(self, *args, **kwargs):
        super(Navigation, self).__init__(*args, **kwargs)

        self.setFixedHeight(px(36))

        self.menu_button = IconButton(
            icon='menu',
            icon_size=(24, 24),
            parent=self,
        )
        self.home_button = IconButton(
            icon='home',
            icon_size=(24, 24),
            parent=self,
        )

        self.crumbs = Crumbs(parent=self)

        # TODO: Trash these temp items
        self.crumbs.add('NY')
        self.crumbs.add('Project_A')
        self.crumbs.add('assets')
        self.crumbs.add('Asset_A')

        self.bookmark_button = IconButton(
            icon='bookmark',
            icon_size=(24, 24),
            parent=self,
        )

        self.layout = HBarLayout(parent=self)
        self.layout.setContentsMargins(*px(16, 0, 16, 0))
        self.layout.left.addWidget(self.menu_button)
        self.layout.left.addWidget(self.home_button)
        self.layout.center.addWidget(self.crumbs)
        self.layout.center.setAlignment(QtCore.Qt.AlignLeft)
        self.layout.right.addWidget(self.bookmark_button)
        self.setLayout(self.layout)


class Crumbs(Widget, QtWidgets.QWidget):

    css_id = 'crumbs'
    css_properties = {}

    def __init__(self, *args, **kwargs):
        super(Crumbs, self).__init__(*args, **kwargs)

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding,
        )

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(QtCore.Qt.AlignLeft)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

    def clear(self):
        while self.layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def add(self, label):
        crumb = Crumb(label, parent=self)
        self.layout.addWidget(crumb)
        return crumb


class Crumb(Widget, QtWidgets.QWidget):

    css_id = 'crumb'

    def __init__(self, label, *args, **kwargs):
        super(Crumb, self).__init__(*args, **kwargs)

        self.label = QtWidgets.QPushButton(label, parent=self)
        self.label.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Expanding,
        )

        self.menu = QtWidgets.QMenu(parent=self)

        # TODO: Temporary menu items
        self.menu.addAction('Menu Item A')
        self.menu.addAction('Menu Item B')
        self.menu.addAction('Menu Item C')
        self.menu.addAction('Menu Item D')
        self.menu.setWindowFlags(
            self.menu.windowFlags() | QtCore.Qt.NoDropShadowWindowHint
        )

        self.arrow = QtWidgets.QPushButton(parent=self)
        self.arrow.setFlat(True)
        self.arrow.setFixedWidth(16)
        self.arrow.setMenu(self.menu)
        self.arrow.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Expanding,
        )

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Expanding,
        )

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.arrow)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(*px(0, 6, 0, 6))
        self.setLayout(self.layout)
