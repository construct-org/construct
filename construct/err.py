'''
errors and exceptions
=====================
All errors and exceptions in Construct are subclasses of ConstructError. This
allows you to easily catch all exceptions raised by construct like so:

    from construct import Construct, ConstructError
    construct = Construct()

    try:
        construct.new_project(root='./my_project')
    except ConstructError:
        # do something
        raise

'''


class ConstructError(Exception):
    '''Base class for all Construct exceptions'''


class InvalidPluginPath(ConstructError):
    '''Raised when a plugin path does not exist'''


class ValidationError(ConstructError):
    '''Raised when an :class:`Action` is instantiated with arguments that do
    not match the parameters specified in :attr:`Action.parameters`'''


class ParameterError(ConstructError):
    '''Raise when a :attr:`Action.parameters` is defined incorrectly'''


class RegistrationError(ConstructError):
    '''Raised when a plugin raises an exception during registration'''


class ConnectError(ConstructError):
    '''Raised when :meth:`ActionHub.connect` fails'''


class InvalidIdentifier(ConstructError):
    '''Raised when :class:`ActionHub` receives an invalid Action identifier'''


class ActionUnavailable(ConstructError):
    '''Raised when an Action is sent even though it is unavailable in the
    current context'''


class ExtractorError(ConstructError):
    '''Raised when an action_router encounters an error during extraction'''


class InjectorError(ConstructError):
    '''Raised when an action_router encounters an error during injection'''


class ActionError(ConstructError):
    '''Raised when an action fails'''


class TimeoutError(ConstructError):
    '''Raised when task times out'''
