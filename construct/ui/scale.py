# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import absolute_import


def dpi():
    '''Get screen DPI to scale UI independent of monitor size.'''

    from Qt import QtWidgets

    app = QtWidgets.QApplication.instance()
    if app:
        return float(app.desktop().logicalDpiX())
    return 96.0


def factor(factor=[]):
    '''Get UI scale factor'''

    if not factor:
        factor.append((dpi() / 96.0))
    return factor[0]


def pix(value):
    '''Scale a pixel value based on screen dpi.'''

    return factor() * value


def pt(value):
    '''Scale a point value based on screen dpi.'''

    return factor() * value * 1.33
