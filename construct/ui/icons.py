# -*- coding: utf-8 -*-

from Qt.QtGui import (
    QIconEngine,
    QIcon,
    QColor,
    QImage,
    QPixmap,
    QPainter,
)
from Qt import QtCore
from Qt.QtSvg import (
    QSvgRenderer,
)


class SvgIconEngine(QIconEngine):
    '''Handles painting of SVG icons.'''

    def __init__(self, svg_file, parent=None):
        super(SvgIconEngine, self).__init__()
        self.svg_file = svg_file
        self.svg = QSvgRenderer(self.svg_file)
        self.parent = parent

    def pixmap(self, size, mode, state):
        img = QImage(size, QImage.Format_ARGB32)
        img.fill(QColor(0, 0, 0, 0))
        pix = QPixmap.fromImage(img)
        painter = QPainter(pix)
        self.paint(painter, pix.rect(), QtCore.Qt.AlignCenter, mode, state)
        return pix

    def paint(self, painter, rect, alignment, mode, state):
        if self.parent:
            # Set color from parent
            painter.setPen(self.parent.palette().text().color())
        self.svg.render(painter, rect)


class SvgIcon(QIcon):
    '''A QIcon that renders a styled svg.

    Arguments:
        svg_file: Path to svg file
        parent: Parent widget used for coloring
    '''

    def __init__(self, svg_file, parent=None):
        super(SvgIcon, self).__init__(SvgIconEngine(svg_file, parent))
        self.svg_file = svg_file


class FontIconEngine(QIconEngine):
    '''Handles painting of Font Icons.'''

    def __init__(self, char, family, parent=None):
        super(FontIconEngine, self).__init__()
        self.char = char
        self.family = family
        self.parent = parent

    def pixmap(self, size, mode, state):
        img = QImage(size, QImage.Format_ARGB32)
        img.fill(QColor(0, 0, 0, 0))
        pix = QPixmap.fromImage(img)
        painter = QPainter(pix)
        self.paint(painter, pix.rect(), QtCore.Qt.AlignCenter, mode, state)
        return pix

    def paint(self, painter, rect, alignment, mode, state):
        font = painter.font()
        font.setPixelSize(max(rect.width(), rect.height()))
        font.setFamily(self.family)
        painter.setFont(font)
        if self.parent:
            # Set color from parent
            painter.setPen(self.parent.palette().text().color())
        painter.drawText(rect, alignment, self.char)


class FontIcon(QIcon):
    '''A QIcon that renders a styled font icon glyph.

    Arguments:
        family: Font family
        char: Unicode character
        parent: Parent widget used for coloring
    '''

    def __init__(self, char, family=None, parent=None):
        family = family or 'construct'
        super(FontIcon, self).__init__(FontIconEngine(char, family, parent))
        self.family = family
        self.char = char

