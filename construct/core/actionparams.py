# -*- coding: utf-8 -*-
from __future__ import absolute_import
import string
from construct.err import ParameterError, ValidationError

REQUIRED_OPTIONS = ['type', 'label']
OPTIONS = ['type', 'label', 'default', 'required']
VALID_CHARACTERS = string.ascii_lowercase + string.digits + '_'


def validate(parameters):
    '''Validate Action parameters dict

    Arguments:
        parameters (dict): describes parameters of a callable:

        {
            'str_param': {
                'name': 'Str Param',
                'type': str,
                'required': True,
                'validator': lambda x: 1 < len(x) < 36
            },
            'int_param': {
                'name': 'Int Param',
                'type': int,
                'required': False,
                'default': 1
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

    >>> parameters = {'arg': {'name': 'Arg', 'default': 1.0}}
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

    for name, options in parameters.items():

        validator = options.get('validator', None)
        required = options.get('required', False)
        type_ = options['type']
        value = kwargs.get(name, None)

        if value is None and required:
            raise ValidationError('Missing required argument: ', name)
        elif value is None and not required:
            continue

        if not isinstance(value, options['type']):
            raise ValidationError(
                '{} must be {} not {}.'.format(name, type_, type(value))
            )

        if validator:
            exc_msg = '{} failed custom validator: {}'.format(name, value)
            try:
                if validate(value) is False:
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
