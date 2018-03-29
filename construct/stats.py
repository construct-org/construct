# -*- coding: utf-8 -*-
from __future__ import absolute_import
from functools import wraps
from construct.constants import TIMER
from construct.utils import get_qualname
from contextlib import contextmanager
import logging


_log = logging.getLogger(__name__)


class Stats(object):
    '''Collection of :class:`Action` execution stats

    Attributes:
        number_of_failures
        number_of_successes
        number_of_skips
        total_execution_time
        group_times
        average_group_time
        task_times
        average_task_time
    '''
    # TODO: Implement stats


@contextmanager
def log_time(msg):

    start_time = TIMER()
    try:
        yield
    finally:
        _log.info('%s: %.8fs', msg, TIMER() - start_time)


def log_call(fn):
    '''Log execution time of a wrapped function'''
    @wraps(fn)
    def _logged_call(*args, **kwargs):
        start_time = TIMER()
        try:
            return fn(*args, **kwargs)
        finally:
            _log.info('%s(): %.8fs', get_qualname(fn), TIMER() - start_time)
    return _logged_call
