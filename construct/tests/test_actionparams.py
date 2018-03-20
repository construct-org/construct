# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from nose.tools import raises
from construct import actionparams
from construct.errors import ValidationError


params_0 = dict()
params_1 = dict(
    str_arg={
        'label': 'String Argument',
        'help': 'A String Argument',
        'required': True,
        'type': str
    },
    int_arg={
        'label': 'Integer Argument',
        'help': 'An Integer Argument',
        'required': True,
        'default': 1,
        'type': int
    },
    float_arg={
        'label': 'Float Argument',
        'help': 'A Float Argument',
        'required': False,
        'default': 10.0,
        'type': float
    },
    dict_arg={
        'label': 'Dict Argument',
        'help': 'A Dict Argument',
        'required': True,
        'type': dict
    }
)


def test_validate_nada():
    '''Validate empty params dict'''
    actionparams.validate(params_0)
    actionparams.validate(params_1)


@raises(ValidationError)
def test_pass_args_to_empty_params():
    '''Validate kwargs against empty params'''
    actionparams.validate_kwargs(params_0, {'invalid': 'kwargs'})


@raises(ValidationError)
def test_missing_required():
    '''Validate kwargs with missing required argument'''
    actionparams.validate_kwargs(
        params_1,
        {'str_arg': 'str', 'dict_arg': {}}
    )


# TODO: Test larger variety of parameter dicts
