# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import absolute_import

# Third party imports
from Qt import QtCore
from Qt.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
)

# Local imports
from .layouts import HBarLayout
from .widgets import (
    H3,
    P,
    Icon,
    IconButton,
)


class BaseDialog(QDialog):
    '''Frameless Dialog

    Arguments:
        parent (QObject)
        f (QtCore.Qt.WindowFlags)
    '''

    def __init__(self, parent=None):
        super(BaseDialog, self).__init__(parent)

        self.setWindowFlags(
            self.windowFlags() |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint
        )

        self.header = QWidget()
        self.header_layout = HBarLayout()
        self.header_layout.setContentsMargins(16, 8, 16, 8)
        self.header.setLayout(self.header_layout)

        self.body = QWidget()
        self.body_layout = QVBoxLayout()
        self.body_layout.setContentsMargins(16, 8, 16, 8)
        self.body.setLayout(self.body_layout)

        self.footer = QWidget()
        self.footer_layout = HBarLayout()
        self.footer_layout.setContentsMargins(16, 8, 16, 8)
        self.footer.setLayout(self.footer_layout)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.header)
        self.layout.addWidget(self.body)
        self.layout.addWidget(self.footer)


class Notification(BaseDialog):

    def __init__(
        self,
        type,
        message,
        title=None,
        icon=None,
        close_icon='icons/close.png',
        parent=None,
    ):
        super(Notification, self).__init__(parent)

        self.type = type.lower()
        self.message = message
        self.icon = icon
        self.close_icon = close_icon
        self.is_brief = title is None or len(message) < 128
        self.title = title or type.title()

        self.setObjectName(self.type)

        if self.icon:
            self.header_layout.left.addWidget(Icon(self.icon))
        if self.close_icon:
            self.header_layout.right.addWidget(IconButton(self.icon))

        if self.is_brief:
            self.header_layout.center.addWidget(P(self.message))
            self.body.hide()
            self.footer.hide()
        else:
            self.header_layout.center.addWidget(H3(self.title))
            self.body_layout.addWidget(P(self.message))
            self.footer.hide()
