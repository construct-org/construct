# -*- coding: utf-8 -*-


# Local imports
from .resources import Resources
from .theme import theme
from .eventloop import requires_event_loop


class UIManager(object):
    '''Manages UI resources, themes, and dialogs.'''

    def __init__(self, api):
        self.api = api
        self.resources = Resources([])
        self.theme = theme

    def load(self):
        self.resources = Resources(self.api.path)
        self.theme.set_resources(self.resources)
        self.api.extend('alert', self.alert)
        self.api.extend('error', self.error)
        self.api.extend('success', self.success)
        self.api.extend('info', self.info)
        self.api.extend('ask', self.ask)

    def unload(self):
        self.resources = Resources([])
        self.theme.set_resources(self.resources)
        self.api.unextend('alert')
        self.api.unextend('error')
        self.api.unextend('success')
        self.api.unextend('ask')

    @requires_event_loop
    def alert(self, message, title=None, short=None):
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
            icon='alert',
            close_icon='close',
            short=short,
        ).exec_()

    @requires_event_loop
    def error(self, message, title=None, short=None):
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
            icon='error',
            close_icon='close',
            short=short,
        ).exec_()

    @requires_event_loop
    def success(self, message, title=None, short=None):
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
            close_icon='check',
            short=short,
        ).exec_()

    @requires_event_loop
    def info(self, message, title=None, short=None):
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
            close_icon='check',
            short=short,
        ).exec_()

    @requires_event_loop
    def ask(self, title, message, yes_label='Yes', no_label='No', icon=None):
        '''Ask a question.

        Arguments:
            title (str): Title
            message (str): Message to display
            yes_label (str): Yes button text
            no_label (str): No button text
            icon (str): Icon to appear in header.
        '''
        from .dialogs import Ask
        return Ask(
            title=title,
            message=message,
            yes_label=yes_label,
            no_label=no_label,
            icon=icon,
        ).exec_()
