# -*- coding: utf-8 -*-

from __future__ import absolute_import

# Third party imports
from Qt import QtCore, QtWidgets

# Local imports
from . import P, Widget
from ..scale import pt
from ..theme import theme


class Button(Widget, QtWidgets.QPushButton):

    css_id = 'text-button'

    def __init__(self, text, icon=None, icon_size=None, **kwargs):
        super(Button, self).__init__(**kwargs)
        self.setFlat(True)
        self.setText(text)
        if icon:
            self.setIcon(theme.icon(icon))
        if icon_size:
            self.setIconSize(QtCore.QSize(pt(icon_size[0]), pt(icon_size[1])))


class ToolButton(Widget, QtWidgets.QPushButton):

    css_id = 'tool-button'

    def __init__(self, text, icon=None, icon_size=None, **kwargs):
        super(ToolButton, self).__init__(**kwargs)

        self.label = P(text, parent=self)
        self.label.setWordWrap(True)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setMouseTracking(False)
        self.label.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.label.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding,
        )

        self.glyph = Glyph(icon, icon_size, parent=self)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(pt(8), pt(8), pt(8), pt(8))
        self.layout.setSpacing(pt(4))
        self.layout.addWidget(self.glyph)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def sizeHint(self):
        return QtCore.QSize(
            self.glyph.size.width() + pt(16),
            self.glyph.size.height() + pt(32),
        )


class Glyph(Widget, QtWidgets.QLabel):

    css_id = 'icon'

    def __init__(self, icon, icon_size, parent=None):
        super(Glyph, self).__init__(parent=parent)

        self.icon = theme.icon(icon, parent=parent)
        if icon_size:
            self.size = QtCore.QSize(pt(icon_size[0]), pt(icon_size[1]))
        else:
            self.size = QtCore.QSize(pt(24), pt(24))
        self.setPixmap(self.icon.pixmap(self.size))
        self.setFixedSize(self.size)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed,
        )
