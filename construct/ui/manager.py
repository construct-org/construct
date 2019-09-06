# -*- coding: utf-8 -*-


# Local imports
from .resources import Resources
from .theme import theme
from .eventloop import starts_event_loop


class UIManager(object):
    '''Manages UI resources, themes, and dialogs.'''

    def __init__(self, api):
        self.api = api
        self.resources = Resources(self.api.path)
        self.theme = theme

    def load(self):
        self.theme.set_resources(self.resources)
        self.api.extend('alert', self.alert)
        self.api.extend('error', self.error)
        self.api.extend('success', self.success)
        self.api.extend('info', self.info)

    def unload(self):
        self.theme.set_resources(Resources([]))
        self.api.unextend('alert')
        self.api.unextend('error')
        self.api.unextend('success')
        self.api.unextend('info')

    @starts_event_loop
    def alert(self, message, title=None):
        '''Create an alert dialog.

        Arguments:
            message (str): Message to display
            title (str): Optional title
        '''
        from .dialogs import Notification
        return Notification(
            type='alert',
            message=message,
            title=title,
            icon='icons/alert.svg',
            close_icon='icons/close.svg',
        ).exec_()

    @starts_event_loop
    def error(self, message, title=None):
        '''Create an error dialog.

        Arguments:
            message (str): Message to display
            title (str): Optional title
        '''
        from .dialogs import Notification
        return Notification(
            type='error',
            message=message,
            title=title,
            icon='icons/error.svg',
            close_icon='icons/close.svg',
        ).exec_()

    @starts_event_loop
    def success(self, message, title=None):
        '''Create a success dialog.

        Arguments:
            message (str): Message to display
            title (str): Optional title
        '''
        from .dialogs import Notification
        return Notification(
            type='success',
            message=message,
            title=title,
            close_icon='icons/close.svg',
        ).exec_()

    @starts_event_loop
    def info(self, message, title=None):
        '''Create an info dialog.

        Arguments:
            message (str): Message to display
            title (str): Optional title
        '''
        from .dialogs import Notification
        return Notification(
            type='info',
            message=message,
            title=title,
            close_icon='icons/close.svg',
        ).exec_()
