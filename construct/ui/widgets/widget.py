# -*- coding: utf-8 -*-


class Widget(object):
    '''Mixin class for all themable widgets.

    Classes that have Widgets as a base class should set css_id and any
    css_properties used in themeing.

    Example:

        class MyWidget(Widget, QtWidgets.QLabel):

            css_id = 'my_label'
            css_properties = {
                'error': False,
            }

    '''

    css_id = ''
    css_properties = {}

    def __init__(self, *args, **kwargs):
        super(Widget, self).__init__(*args, **kwargs)

        print(self.css_id)
        print(self.css_properties)
        for prop, value in self.css_properties.items():
            self.setProperty(prop, value)

        if self.css_id:
            self.setObjectName(self.css_id)
