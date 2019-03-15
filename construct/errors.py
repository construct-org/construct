# -*- coding: utf-8 -*-
from future.builtins import super


class InvalidSettings(Exception):
    '''Raise when your settings are invalid.'''


class ValidationError(Exception):
    '''Raise when data has invalid keys and values.'''

    def __init__(self, msg, errors):
        super().__init__(msg)
        self.errors = errors
