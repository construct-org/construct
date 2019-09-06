# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import absolute_import

# Third party imports
from Qt import QtCore
from Qt.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QPushButton,
)

# Local imports
from .layouts import HBarLayout
from .widgets import (
    H3,
    P,
)
from .theme import theme
from .scale import pix


class FramelessDialog(QDialog):
    '''Frameless Dialog

    Arguments:
        parent (QObject)
        f (QtCore.Qt.WindowFlags)
    '''

    _resize_area_map = {
        (False, False, False, False): None,
        (True, False, False, False): 'left',
        (True, True, False, False): 'topLeft',
        (False, True, False, False): 'top',
        (False, True, True, False): 'topRight',
        (False, False, True, False): 'right',
        (False, False, True, True): 'bottomRight',
        (False, False, False, True): 'bottom',
        (True, False, False, True): 'bottomLeft'
    }
    _cursor_map = {
        None: QtCore.Qt.ArrowCursor,
        'left': QtCore.Qt.SizeHorCursor,
        'topLeft': QtCore.Qt.SizeFDiagCursor,
        'top': QtCore.Qt.SizeVerCursor,
        'topRight': QtCore.Qt.SizeBDiagCursor,
        'right': QtCore.Qt.SizeHorCursor,
        'bottomRight': QtCore.Qt.SizeFDiagCursor,
        'bottom': QtCore.Qt.SizeVerCursor,
        'bottomLeft': QtCore.Qt.SizeBDiagCursor
    }
    css_id = 'surface'

    def __init__(self, parent=None):
        super(FramelessDialog, self).__init__(parent)

        self._mouse_pressed = False
        self._mouse_position = None
        self._resize_area = None
        self.resize_area_size = 16

        self.setObjectName(self.css_id)
        theme.apply(self)

        self.setWindowFlags(
            self.windowFlags() |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint
        )

        margins = (pix(16), pix(8), pix(16), pix(8))

        self.header = QWidget()
        self.header_layout = HBarLayout()
        self.header_layout.setContentsMargins(*margins)
        self.header.setLayout(self.header_layout)

        self.body = QWidget()
        self.body_layout = QVBoxLayout()
        self.body_layout.setContentsMargins(*margins)
        self.body.setLayout(self.body_layout)

        self.footer = QWidget()
        self.footer_layout = HBarLayout()
        self.footer_layout.setContentsMargins(*margins)
        self.footer.setLayout(self.footer_layout)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.header)
        self.layout.addWidget(self.body)
        self.layout.addWidget(self.footer)
        self.setLayout(self.layout)

    @property
    def resizing(self):
        return bool(self._resize_area)

    def _check_resize_area(self, pos):

        x, y = pos.x(), pos.y()
        self._resize_area = self._resize_area_map[(
            x < self.resize_area_size,
            y < self.resize_area_size,
            x > self.width() - self.resize_area_size,
            y > self.height() - self.resize_area_size,
        )]

    def mousePressEvent(self, event):

        if event.buttons() & QtCore.Qt.LeftButton:
            pos = event.pos()
            self._check_resize_area(pos)
            self._mouse_pressed = True
            self._mouse_position = pos

    def mouseMoveEvent(self, event):

        if not self._mouse_pressed:
            pos = event.pos()
            self._check_resize_area(pos)
            cursor = self._cursor_map.get(self._resize_area)
            self.setCursor(cursor)

        if self._mouse_pressed:
            vector = event.pos() - self._mouse_position
            if self.resizing:
                rect = self.geometry()
                offset = self.mapToParent(self._mouse_position + vector)
                resize_area = self._resize_area.lower()
                if 'left' in resize_area:
                    new_width = rect.width() + rect.left() - offset.x()
                    if new_width > self.minimumWidth():
                        rect.setLeft(offset.x())
                if 'top' in resize_area:
                    new_height = rect.height() + rect.top() - offset.y()
                    if new_height > self.minimumHeight():
                        rect.setTop(offset.y())
                if 'right' in resize_area:
                    rect.setRight(offset.x())
                if 'bottom' in resize_area:
                    rect.setBottom(offset.y())
                self.setGeometry(rect)
            else:
                self.move(self.mapToParent(vector))

    def mouseReleaseEvent(self, event):
        self._mouse_pressed = False
        self._mouse_position = None


class Notification(FramelessDialog):

    def __init__(
        self,
        type,
        message,
        title=None,
        icon=None,
        close_icon=None,
        parent=None,
    ):
        super(Notification, self).__init__(parent)

        self.type = type.lower()
        self.message = message

        if icon:
            self.icon = theme.icon(icon, parent=self)
        else:
            self.icon = None

        self.close_icon = theme.icon(close_icon or 'close', parent=self)
        self.close_button = QPushButton(parent=self)
        self.close_button.setObjectName('icon')
        self.close_button.setIcon(self.close_icon)
        self.close_button.setIconSize(QtCore.QSize(pix(24), pix(24)))
        self.close_button.setFlat(True)
        self.close_button.clicked.connect(self.accept)

        self.is_brief = title is None or len(message) < 128
        self.title = title or type.title()

        self.setObjectName(self.type)

        # if self.icon:
        #     self.header_layout.left.addWidget(self.icon)
        if self.close_icon:
            self.header_layout.right.addWidget(self.close_button)

        if self.is_brief:
            self.header_layout.center.addWidget(P(self.message))
            self.body.hide()
            self.footer.hide()
        else:
            self.header_layout.center.addWidget(H3(self.title))
            self.body_layout.addWidget(P(self.message))
            self.footer.hide()
