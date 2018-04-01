# -*- coding: utf-8 -*-
'''
errors and exceptions
=====================
All errors and exceptions in Construct are subclasses of ConstructError.
Errors that modify Action execution are subclasses of ActionControlFlowError.
'''


class ConstructError(Exception):
    '''Base class for all Construct exceptions'''


class InvalidPluginPath(ConstructError):
    '''Raised when a plugin path does not exist'''


class ParameterError(ConstructError):
    '''Raise when a :attr:`Action.parameters` is defined incorrectly'''


class RegistrationError(ConstructError):
    '''Raised when a plugin raises an exception during registration'''


class ContextError(ConstructError):
    '''Raised when an error in Context is encountered'''


class ConfigurationError(ConstructError):
    '''Raised when an Entry or Construct is misconfigured'''


class ActionUnavailable(ConstructError):
    '''Raised when an Action is sent even though it is unavailable in the
    current context'''


class ActionError(ConstructError):
    '''Raised when an action fails'''


class TaskError(ConstructError):
    '''Raised when a task is misconfigured'''


class TemplateError(ConstructError):
    '''Raised when a folder template, or path template error occurs'''


class ActionControlFlowError(ConstructError):
    '''
    Raised by Tasks to control Action execution...
    '''

    def __init__(self, *args, **kwargs):
        import construct
        self.ctx = construct.get_context()
        self.request = construct.get_request()
        super(ActionControlFlowError, self).__init__(*args, **kwargs)


class ValidationError(ActionControlFlowError):
    '''Raised when an :class:`Action` is instantiated with arguments that do
    not match the parameters specified in :attr:`Action.parameters`'''

    def __init__(self, *args, **kwargs):
        self.selection = kwargs.pop('selection', [])
        super(ValidationError, self).__init__(*args, **kwargs)


class TimeoutError(ActionControlFlowError):
    '''Raised when a request times out'''


class Abort(ActionControlFlowError):
    '''
    Raised by a Task to notify the ActionRunner that a critical error has
    occured. The ActionRunner will stop executing tasks and raise the error.
    '''


class Fail(ActionControlFlowError):
    '''
    Raised by a Task to notify the ActionRunner that the Task has failed, but,
    the ActionRunner should continue.
    '''


class Pause(ActionControlFlowError):
    '''
    Raised by a Task to pause the ActionRunner.
    '''


class Confirm(ActionControlFlowError):
    '''
    Raised by a Task to request confirmation of specific items from user.
    '''

    def __init__(self, items, *args, **kwargs):
        self.items = items
        super(Confirm, self).__init__(*args, **kwargs)
