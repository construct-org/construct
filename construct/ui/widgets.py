# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import absolute_import

# Third party imports
from Qt import QtCore, QtWidgets

# Local imports
from .theme import theme
from .scale import pt


__all__ = [
    'H1',
    'H2',
    'H3',
    'H4',
    'H5',
    'P',
]


class BaseLabel(QtWidgets.QLabel):

    css_id = ''

    def __init__(self, *args, **kwargs):
        super(BaseLabel, self).__init__(*args, **kwargs)
        self.setObjectName(self.css_id)


class H1(BaseLabel):
    css_id = 'h1'


class H2(BaseLabel):
    css_id = 'h2'


class H3(BaseLabel):
    css_id = 'h3'


class H4(BaseLabel):
    css_id = 'h2'


class H5(BaseLabel):
    css_id = 'h3'


class P(BaseLabel):
    css_id = 'p'

    def __init__(self, *args, **kwargs):
        super(P, self).__init__(*args, **kwargs)
        self.setWordWrap(True)


class Button(QtWidgets.QPushButton):
    css_id = 'text-button'

    def __init__(self, text, icon=None, icon_size=None, **kwargs):
        super(Button, self).__init__(**kwargs)
        self.setObjectName(self.css_id)
        self.setText(text)
        if icon:
            self.setIcon(theme.icon(icon))
        if icon_size:
            self.setIconSize(QtCore.QSize(pt(icon_size[0]), pt(icon_size[1])))


class ToolButton(QtWidgets.QPushButton):
    css_id = 'tool-button'

    def __init__(self, text, icon=None, icon_size=None, **kwargs):
        super(ToolButton, self).__init__(**kwargs)
        self.setObjectName(self.css_id)

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


class Glyph(QtWidgets.QLabel):
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
