# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import absolute_import

# Third party imports
from Qt import QtCore
from Qt.QtWidgets import (
    QBoxLayout
)

# Local imports


class BarLayout(QBoxLayout):
    '''BarLayout like BoxLayout but with 3 sub layouts allowing users to add
    widgets to the start, middle and end of the layout.

    |start | -------- middle -------- | end|

    Attributes:
        start - QBoxLayout with default direction set to LeftToRight
        middle - QBoxLayout with default direction set to LeftToRight
        end - QBoxLayout with default direction set to LeftToRight
    '''

    def __init__(self, direction=None, parent=None):
        super(BarLayout, self).__init__(parent=parent)

        self.start = QBoxLayout()
        self.start.setSpacing(0)
        self.left = self.start
        self.top = self.start

        self.middle = QBoxLayout()
        self.middle.setSpacing(0)
        self.center = self.middle

        self.end = QBoxLayout()
        self.end.setSpacing(0)
        self.right = self.end
        self.bottom = self.end

        self.addLayout(self.start)
        self.addLayout(self.middle)
        self.addLayout(self.end)

        self.setStretch(1, 1)
        self.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)

        direction = direction or self.LeftToRight
        self.setDirection(direction)

    def setDirection(self, direction):
        '''Realign sub-layouts based on direction'''

        if direction in (self.LeftToRight, self.RighToLeft):
            self.start.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
            self.middle.setAlignment(QtCore.Qt.AlignCenter)
            self.end.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        elif direction in (self.TopToBottom, self.BottomToTop):
            self.start.setAlignment(QtCore.Qt.AlignTop|QtCore.Qt.AlignHCenter)
            self.middle.setAlignment(QtCore.Qt.AlignCenter)
            self.end.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignHCenter)
        else:
            raise ValueError(
                'Got %s expected QBoxLayout.Direction' % direction
            )

        self.start.setDirection(direction)
        self.middle.setDirection(direction)
        self.end.setDirection(direction)
        super(BarLayout, self).setDirection(direction)


class HBarLayout(BarLayout):
    '''Horizontal BarLayout.

    Attributes:
        left - VBoxLayout alignment set to left
        center - VBoxLayout alignment set to center
        right - VBoxLayout alignment set to right
    '''

    def __init__(self, parent=None):
        super(HBarLayout, self).__init__(BarLayout.LeftToRight, parent)


class VBarLayout(BarLayout):
    '''Vertical BarLayout.

    Attributes:
        top - VBoxLayout alignment set to top
        center - VBoxLayout alignment set to center
        bottom - VBoxLayout alignment set to bottom
    '''

    def __init__(self, parent=None):
        super(VBarLayout, self).__init__(BarLayout.TopToBottom, parent)
