# -*- coding: utf-8 -*-

# Third party imports
from Qt import QtWidgets

# Local imports
from ..scale import px
from . import Widget


__all__ = [
    'HLine',
    'VLine',
]


class HLine(Widget, QtWidgets.QFrame):

    css_id = 'line'

    def __init__(self, thickness=1, *args, **kwargs):
        super(HLine, self).__init__(*args, **kwargs)

        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed,
        )
        self.setFixedHeight(px(thickness))


class VLine(Widget, QtWidgets.QFrame):

    css_id = 'line'

    def __init__(self, thickness=1, *args, **kwargs):
        super(HLine, self).__init__(*args, **kwargs)

        self.setFrameShape(QtWidgets.QFrame.VLine)
        self.setSizePolicy(
            QtCore.QSizePolicy.Fixed,
            QtGui.QSizePolicy.Expanding,
        )
        self.setFixedWidth(px(thickness))
