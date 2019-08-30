# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import absolute_import, print_function
import os
import sys

# Third party imports
import qtsass
from Qt.QtGui import (
    QFont,
    QFontDatabase,
)
from Qt.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)


this_dir = os.path.dirname(__file__)
icon_map = {}
css = ''


class Icon(QLabel):

    def __init__(self, icon, parent=None):
        super(Icon, self).__init__(parent=parent)

        if icon in icon_map:
            self.setText(icon_map[icon])

        self.setObjectName('icon')


def load():
    global icon_map
    global css

    css = custom_style()

    with open(os.path.join(this_dir, '_icons.scss'), 'r') as f:
        lines = f.readlines()

    for line in lines:

        if not line.startswith('$icon-'):
            continue

        line = line[1:].strip(' $;\n')
        name, c = line.split(':')
        c = c.strip(' "').replace('\\e', '\\ue')
        icon_map[name.strip()] = c.encode().decode('unicode_escape')

    QFontDatabase().addApplicationFont('construct.ttf')


def custom_style(**colors):

    scss = ""
    for k, v in colors.items():
        scss += "$%s: %s;\n"
    scss += "@import '_base';"

    css = qtsass.compile(
        scss,
        include_paths=[this_dir]
    )
    return css


def random_style(widget):
    from random import choice

    styles = ['surface', 'alert', 'background', 'primary']
    widget.setObjectName(choice(styles))
    widget.setStyleSheet(widget.styleSheet())


def main():

    app = QApplication(sys.argv)
    load()

    widget = QWidget()
    widget.setLayout(QHBoxLayout())
    widget.setObjectName('alert')
    widget.setStyleSheet(css)

    for icon in icon_map.keys():
        widget.layout().addWidget(Icon(icon))

    styler = QPushButton('Random Style')
    widget.layout().addWidget(styler)
    styler.clicked.connect(lambda: random_style(widget))

    widget.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
