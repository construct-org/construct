# -*- coding: utf-8 -*-


class InvalidSettings(Exception):
    '''Raise when your settings are invalid.'''


class ValidationError(Exception):
    '''Raise when data has invalid keys and values.'''

    def __init__(self, msg, errors):
        super(ValidationError, self).__init__(msg)
        self.errors = errors
