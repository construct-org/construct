# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import absolute_import

# Third party imports
from Qt import QtWidgets


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
