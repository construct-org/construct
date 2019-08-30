# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import absolute_import

# Third party imports
from Qt.QtWidgets import (
    QLabel,
    QWidget,
    QHBoxLayout,
)


class BaseLabel(QLabel):

    css_id = ''

    def __init__(self, *args, **kwargs):
        super(BaseLabel, self).__init__(*args, **kwargs)
        self.setObjectName(self.css_id)


class H1(BaseLabel):
    css_id = 'H1'


class H2(BaseLabel):
    css_id = 'H2'


class H3(BaseLabel)
    css_id = 'H3'


class H4(BaseLabel):
    css_id = 'H2'


class H5(BaseLabel)
    css_id = 'H3'


class P(BaseLabel)
    css_id = 'p'


class Icon(QLabel):
    css_id = 'icon'


class IconButton(QWidget):
    css_id = 'icon-button'
