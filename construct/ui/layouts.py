# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import absolute_import

# Third party imports
from Qt import QtCore
from Qt.QtWidgets import (
    QBoxLayout,
    QLayout,
    QStyle,
    QSizePolicy
)

# Local imports
from .scale import pt


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
        direction = direction or self.LeftToRight
        super(BarLayout, self).__init__(direction, parent)

        self.start = QBoxLayout(direction)
        self.start.setSpacing(pt(8))
        self.left = self.start
        self.top = self.start

        self.middle = QBoxLayout(direction)
        self.middle.setSpacing(pt(8))
        self.center = self.middle

        self.end = QBoxLayout(direction)
        self.end.setSpacing(pt(8))
        self.right = self.end
        self.bottom = self.end

        self.addLayout(self.start)
        self.addLayout(self.middle)
        self.addLayout(self.end)

        self.setStretch(1, 1)
        self.setSpacing(pt(8))
        self.setContentsMargins(0, 0, 0, 0)

        self.setDirection(direction)

    def count(self):
        '''Sum of the count of all sub layouts'''
        return self.start.count() + self.middle.count() + self.end.count()

    def setDirection(self, direction):
        '''Realign sub-layouts based on direction'''

        if direction in (self.LeftToRight, self.RightToLeft):
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
        left - QBoxLayout alignment set to left
        center - QBoxLayout alignment set to center
        right - QBoxLayout alignment set to right
    '''

    def __init__(self, parent=None):
        super(HBarLayout, self).__init__(BarLayout.LeftToRight, parent)


class VBarLayout(BarLayout):
    '''Vertical BarLayout.

    Attributes:
        top - QBoxLayout alignment set to top
        center - QBoxLayout alignment set to center
        bottom - QBoxLayout alignment set to bottom
    '''

    def __init__(self, parent=None):
        super(VBarLayout, self).__init__(BarLayout.TopToBottom, parent)


class FlowLayout(QLayout):
    '''A Layout that wraps widgets on overflow.
    ____________
    | [] [] [] |
    | [] [] [] |
    | [] []    |
    ------------
    '''

    def __init__(self, margin=16, hspacing=8, vspacing=8, parent=None):
        super(FlowLayout, self).__init__(parent=parent)
        self._margin = pt(margin)
        self._hspacing = pt(hspacing)
        self._vspacing = pt(vspacing)
        self._items = []
        self.setContentsMargins(margin, margin, margin, margin)

    def __del__(self):
        while self.count():
            item = self.takeAt(0)
            del item

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        try:
            return self._items[index]
        except IndexError:
            return

    def takeAt(self, index):
        return self._items.pop(index)

    def horizontalSpacing(self):
        return self._hspacing

    def verticalSpacing(self):
        return self._vspacing

    def expandingDirections(self):
        return QtCore.Qt.Horizontal

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(
            QtCore.QRect(0, 0, width, 0),
            True
        )

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()
        for item in self._items:
            size.expandedTo(item.minimumSize())

        margins = self.contentsMargins()
        size += QtCore.QSize(
            margins.left() + margins.right(),
            margins.top() + margins.bottom()
        )
        return size

    def doLayout(self, rect, testOnly=False):

        m = self.contentsMargins()
        r = rect.adjusted(m.left(), m.top(), -m.right(), -m.bottom())
        x, y = r.x(), r.y()
        rows = []
        row = {'items': [], 'height': 0, 'space': 0, 'count': 0}
        rows.append(row)

        for item in self._items:
            w = item.widget()
            width, height = w.sizeHint().width(), w.sizeHint().height()
            space = self.horizontalSpacing()
            if space < 0:
                space = w.style().layoutSpacing(
                    QSizePolicy.QPushButton,
                    QSizePolicy.QPushButton,
                    QtCore.Qt.Horizontal,
                )

            if x + width < r.right():
                row['items'].append(item)
                row['height'] = max(row['height'], height)
                row['space'] += space
                row['count'] += 1
                x += width + space
            else:
                row['space'] += r.right() - x - space
                row = {
                    'items': [item],
                    'height': height,
                    'space': space,
                    'count': 1
                }
                rows.append(row)
                x = r.x() + width + space

        if testOnly:
            if len(rows) < 2:
                vspace = 0
            else:
                vspace = (len(rows) - 1) * self.verticalSpacing()
            vmargins = m.top() + m.bottom()
            return sum([r['height'] for r in rows]) + vspace + vmargins

        x, y = r.x(), r.y()
        for row in rows:

            if row['count'] < 2:
                space = 0
            else:
                space = row['space'] / len(row['items']) - 1

            for item in row['items']:
                item.setGeometry(QtCore.QRect(
                    QtCore.QPoint(x, y),
                    item.sizeHint()
                ))
                x += item.sizeHint().width() + space

            x = r.x()
            y += row['height'] + self.verticalSpacing()
