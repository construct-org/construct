# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from werkzeug.local import Local, LocalStack, LocalProxy
from aenum import IntFlag, auto
__all__ = ['status', 'g', 'context', 'request', 'current_cons']

class status(IntFlag):

    WAITING = auto()
    READY = auto()
    RUNNING = auto()
    SUCCESS = auto()
    SKIPPED = auto()
    FAILED = auto()
    DONE_STATUSES = SUCCESS | FAILED


g = Local()

_cons_stack = LocalStack()
current_cons = LocalProxy(_cons_stack, 'top')

_ctx_stack = LocalStack()
context = LocalProxy(_ctx_stack, 'top')

_req_stack = LocalStack()
request = LocalProxy(_req_stack, 'top')
