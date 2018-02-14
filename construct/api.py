# -*- coding: utf-8 -*-
from __future__ import absolute_import
from construct import compat
from construct.err import *
from construct.construct import Construct
from construct.action import *
from construct.actionhub import *
from construct.actionloop import *
from construct.context import *
from construct.constants import *
from construct.signal import *
from construct.tasks import *
from construct import (
    actionparams,
    types,
    util,
)


def init(*args, **kwargs):
    '''Initialize Construct, passing args and kwargs to Construct and setting
    the Construct.active attribute

    Parameters:
        args: Args to pass to Construct
        kwargs: Kwargs to pass to Construct

    Returns:
        Construct instance

    Raises:
        RuntimeError: When Construct.active already exists
    '''

    if Construct.active:
        raise RuntimeError('Construct has already been initialized.')

    inst = Construct(*args, **kwargs)
    Construct.active = inst
    return inst


def get():
    '''Get the active Construct instance'''

    if not Construct.active:
        raise RuntimeError('Construct has not been initialized.')

    return Construct.active



def set(inst):
    '''Set the active Construct instance

    Parameters:
        inst (Construct): Instance of Construct
    '''

    Construct.active = inst


def get_context():
    '''Get the active Construct instance's context'''

    return Construct.active.get_context()
