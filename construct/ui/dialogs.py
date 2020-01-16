# -*- coding: utf-8 -*-

from __future__ import absolute_import

# Third party imports
from Qt import QtCore, QtGui, QtWidgets

# Local imports
from .layouts import HBarLayout
from .scale import pt
from .theme import theme
from .widgets import H3, P, Button


class FramelessDialog(QtWidgets.QDialog):
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
        super(FramelessDialog, self).__init__(parent=parent)

        self._mouse_pressed = False
        self._mouse_position = None
        self._resize_area = None
        self.resize_area_size = pt(5)
        self.setMouseTracking(True)
        self.setWindowFlags(
            QtCore.Qt.Dialog |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint
        )
        self.setObjectName(self.css_id)
        self.setWindowTitle('construct')
        self.setWindowIcon(theme.icon('brand/construct_icon-white.png'))
        theme.apply(self)

        margins = (pt(10), pt(10), pt(10), pt(10))

        self.header = QtWidgets.QWidget()
        self.header_layout = HBarLayout()
        self.header.setLayout(self.header_layout)

        self.body = QtWidgets.QWidget()
        self.body_layout = QtWidgets.QVBoxLayout()
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(pt(10))
        self.body.setLayout(self.body_layout)

        self.footer = QtWidgets.QWidget()
        self.footer_layout = HBarLayout()
        self.footer.setLayout(self.footer_layout)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(*margins)
        self.layout.setSpacing(pt(8))
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
            offset = event.globalPos()

            if self.resizing:
                min_width = self.minimumWidth()
                min_height = self.minimumHeight()
                rect = self.geometry()
                resize_area = self._resize_area.lower()

                if 'left' in resize_area:
                    new_width = rect.width() - vector.x()
                    if new_width > min_width:
                        rect.setLeft(offset.x())

                if 'right' in resize_area:
                    new_width = rect.width() + vector.x()
                    if new_width > min_width:
                        rect.setRight(offset.x())

                if 'top' in resize_area:
                    new_height = rect.height() - vector.y()
                    if new_height > min_height:
                        rect.setTop(offset.y())

                if 'bottom' in resize_area:
                    new_height = rect.height() + vector.y()
                    if new_height > min_height:
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
        short=None,
        parent=None,
    ):
        super(Notification, self).__init__(parent=parent)

        self.setObjectName(type.lower())
        self.setMinimumWidth(pt(272))

        self.header_message = P(message, parent=self)
        self.header_message.setAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.body_message = P(message, parent=self)
        self.body_message.setAlignment(QtCore.Qt.AlignLeft)
        self.title = H3(title or type.title(), parent=self)
        self.title.setAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )

        # TODO: Creat icon widget
        self.icon_widget = QtWidgets.QPushButton(parent=self)
        self.icon_widget.hide()
        self.icon_widget.setObjectName('icon')
        self.icon_widget.setFlat(True)
        self.icon_widget.setDisabled(True)
        self.set_icon(icon)

        self.close_button = QtWidgets.QPushButton(parent=self)
        self.close_button.setObjectName('icon')
        self.close_button.setFlat(True)
        self.close_button.clicked.connect(self.accept)
        self.set_close_icon(close_icon)

        self.header_layout.left.addWidget(self.icon_widget)
        self.header_layout.center.addWidget(self.header_message, stretch=1)
        self.header_layout.center.addWidget(self.title, stretch=1)
        self.header_layout.right.addWidget(self.close_button)
        self.body_layout.addWidget(self.body_message, stretch=1)

        if short is not None:
            self.set_short(short)
        else:
            self.set_short(len(message) < 72)

    def set_short(self, value):
        self.is_short = value
        if self.is_short:
            self.header_message.show()
            self.title.hide()
            self.body.hide()
            self.footer.hide()
            self.adjustSize()
        else:
            self.title.show()
            self.footer.setVisible(self.footer_layout.count())
            self.body.show()
            self.header_message.hide()
            self.adjustSize()

    def set_type(self, type):
        self.setObjectName(type.lower())
        theme.apply(self)

    def set_icon(self, icon):
        if icon:
            self.icon = theme.icon(icon, parent=self.icon_widget)
            self.icon_widget.setIcon(self.icon)
            self.icon_widget.setIconSize(QtCore.QSize(pt(24), pt(24)))
            self.icon_widget.show()
            self.title.setAlignment(QtCore.Qt.AlignCenter)
        else:
            self.icon = None
            self.icon_widget.hide()
            self.header_message.setAlignment(
                QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
            )
            self.title.setAlignment(
                QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
            )

    def set_close_icon(self, icon):
        self.close_icon = theme.icon(
            icon or 'close',
            parent=self.close_button
        )
        self.close_button.setIcon(self.close_icon)
        self.close_button.setIconSize(QtCore.QSize(pt(24), pt(24)))


class Ask(FramelessDialog):

    def __init__(
        self,
        title,
        message,
        yes_label='Yes',
        no_label='No',
        icon=None,
        parent=None,
    ):
        super(Ask, self).__init__(parent=parent)
        self.setObjectName('surface')
        self.setMinimumWidth(pt(272))

        self.title = H3(title, parent=self)
        self.title.setAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.body_message = P(message, parent=self)
        self.body_message.setAlignment(QtCore.Qt.AlignLeft)

        # TODO: Creat icon widget
        self.icon_widget = QtWidgets.QPushButton(parent=self)
        self.icon_widget.hide()
        self.icon_widget.setObjectName('icon')
        self.icon_widget.setFlat(True)
        self.icon_widget.setDisabled(True)
        self.set_icon(icon)

        self.yes_button = Button(yes_label, parent=self)
        self.yes_button.clicked.connect(self.accept)

        self.no_button = Button(no_label, parent=self)
        self.no_button.clicked.connect(self.reject)

        self.header_layout.left.addWidget(self.icon_widget)
        self.header_layout.center.addWidget(self.title, stretch=1)
        self.body_layout.addWidget(self.body_message, stretch=1)
        self.footer_layout.right.addWidget(self.yes_button)
        self.footer_layout.right.addWidget(self.no_button)

        self.adjustSize()

    def set_icon(self, icon):
        if icon:
            self.icon = theme.icon(icon, parent=self.icon_widget)
            self.icon_widget.setIcon(self.icon)
            self.icon_widget.setIconSize(QtCore.QSize(pt(24), pt(24)))
            self.icon_widget.show()
        else:
            self.icon = None
            self.icon_widget.hide()
