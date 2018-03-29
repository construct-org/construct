# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

__all__ = ['validate', 'validate_kwargs', 'get_defaults']

import string
from construct.errors import ParameterError, ValidationError
from fstrings import f

REQUIRED_OPTIONS = ['type', 'label']
OPTIONS = ['type', 'label', 'default', 'required', 'options']
# TODO: Add an additional option to handle coercions?
#       coercions=[(TYPE, CONVERTER)...]
VALID_CHARACTERS = string.ascii_lowercase + string.digits + '_'


def validate(parameters):
    '''Validate Action parameters dict

    Arguments:
        parameters (dict): describes parameters of a callable:

        {
            'str_param': {
                'label': 'Str Param',
                'type': str,
                'required': True,
                'validator': lambda x: 1 < len(x) < 36,
                'help': 'This is a required string parameter'
            },
            'int_param': {
                'label': 'Int Param',
                'type': int,
                'required': False,
                'default': 1,
                'help': 'This is an unrequired int parameter'
            },
            ...
        }

    Returns:
        True if parameters are valid

    Raises:
        ParameterError: describing invalid parameter
    '''

    for name, options in parameters.items():

        chars = set(name)
        invalid_chars = chars - set(VALID_CHARACTERS)
        if invalid_chars:
            raise ParameterError(
                name, ' contains invalid chars: ', ''.join(invalid_chars)
            )

        opt_names = set(options.keys())
        missing_options = set(REQUIRED_OPTIONS) - opt_names
        if missing_options:
            raise ParameterError(
                name, ' missing required options: ', list(missing_options)
            )

        if 'default' in options:
            default = options['default']
            if callable(default):
                pass
            elif not isinstance(default, options['type']):
                raise ParameterError(
                    '{} default value, {}, does not match type, {}'.format(
                        name, default, options['type']
                    )
                )

        validator = options.get('validator', None)
        if validator and not callable(validator):
            raise ParameterError(
                'Validator must be callable: ', name
            )

    return True


def validate_kwargs(parameters, kwargs):
    '''Validate kwargs using Action parameters dict:

    >>> parameters = {'arg': {'name': 'Arg', 'default': 1.0, 'type': float}}
    >>> kwargs = {'arg': 10.0}
    >>> validate_kwargs(parameters, kwargs)
    True

    Arguments:
        parameters (dict): describes parameters of a callable:
        kwargs (dict): function arguments as keyword arguments:

    Returns:
        True

    Raises:
        ValidationError: describing why kwargs is invalid
    '''

    if not parameters and kwargs:
        raise ValidationError(f('Got additional arguments: {kwargs}'))

    for name, options in parameters.items():

        validator = options.get('validator', None)
        required = options.get('required', False)
        type_ = options['type']
        value = kwargs.get(name, None)
        valid_values = options.get('options', None)

        if value is None and required:
            raise ValidationError(f('Missing required argument: {name}'))
        elif value is None and not required:
            continue

        if not isinstance(value, options['type']):
            raise ValidationError(f('{name} must be {type_} not {value}.'))

        if valid_values:
            exc_msg = f('{name} must be one of: {valid_values}')
            if value not in valid_values:
                raise ValidationError(exc_msg)

        if validator:
            exc_msg = f('{name} failed custom validator: {value}')
            try:
                if validator(value) is False:
                    raise ValidationError(exc_msg)
            except:
                raise ValidationError(exc_msg)

    return True


def get_defaults(parameters):
    '''Extract default values from parameters dict.

    >>> parameters = {'arg': {'name': 'Arg', 'default': 1.0}}
    >>> get_defaults(parameters)
    {'arg': 1.0}

    Arguments:
        parameters (dict): describes parameters of a callable:

    Returns:
        dict: Containing name, default value pairs
    '''

    defaults = {}
    for name, options in parameters.items():
        try:
            default = options['default']
            if callable(default):
                default = default()
            defaults[name] = default
        except KeyError:
            continue

    return defaults
