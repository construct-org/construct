# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import time
from timeit import default_timer
from construct import Task, AsyncTask, TimeoutError
from construct.constants import *
from nose.tools import raises


def func_no_args():
    return 'SUCCESS'


def func_w_args(*args, **kwargs):
    return args, kwargs


def func_poll(interval):
    time.sleep(interval)
    return True


def func_raises():
    raise ValueError


def test_call_Task():
    '''Call a Task'''

    t = Task(func_no_args, 'func.no.args', 'function without arguments')
    assert t() == 'SUCCESS'

    t = Task(func_w_args, 'func.w.args', 'function with arguments')
    args, kwargs = ('arg',), {'kwarg': None}
    assert t(*args, **kwargs) == (args, kwargs)


def test_call_AsyncTask():
    '''Call an AsyncTask'''

    t = AsyncTask(func_no_args, 'func.no.args', 'function without arguments')
    assert t() == 'SUCCESS'

    t = AsyncTask(func_w_args, 'func.w.args', 'function with arguments')
    args, kwargs = ('arg',), {'kwarg': None}
    assert t(*args, **kwargs) == (args, kwargs)


def test_Task_request():
    '''Use a task request'''

    t = Task(func_no_args, 'func.no.args', 'function without arguments')
    r = t.request()

    assert r.task is t
    assert r.args == ()
    assert r.kwargs == {}
    assert r.status == WAITING
    assert not r.ready
    assert r.get() == 'SUCCESS'
    assert r.ready
    assert r.status == SUCCESS


@raises(ValueError)
def test_Request_propagate():
    '''Request exception propagation'''

    t = Task(func_raises, 'func.raises', 'Task raises ValueError')

    # Do not propagate
    r = t.request()
    exc = r.get(propagate=False)
    assert r.status == FAILED
    assert exc[0] == ValueError

    # Propagate
    r = t.request()
    r.get()


def test_AsyncTask_request():
    '''Use an async task request'''

    t = AsyncTask(func_poll, 'func.poll', 'Polling task')
    r = t.request(args=(0,))

    assert r.task is t
    assert r.args == (0,)
    assert r.kwargs == {}
    assert r.status == WAITING
    assert not r.ready
    assert r.get()
    assert r.ready
    assert r.status == SUCCESS


@raises(TimeoutError)
def test_AsyncRequest_timeout():
    '''AsyncRequest raises TimeoutError'''

    t = AsyncTask(func_poll, 'func.poll', 'Polling task')
    r = t.request(args=(1,))
    r.get(0)


@raises(ValueError)
def test_AsyncRequest_propagate():
    '''AsyncRequest exception propagation'''

    t = AsyncTask(func_raises, 'func.raises', 'Task raises ValueError')

    # Do not propagate
    r = t.request()
    exc = r.get(propagate=False)
    assert r.status == FAILED
    assert exc[0] == ValueError

    # Propagate
    r = t.request()
    r.get()


def test_AsyncRequest_returns_asap():
    '''AsyncRequest get returns ASAP'''

    t = AsyncTask(func_poll, 'func.poll', 'Polling task')
    r = t.request(args=(0.1,))

    st = default_timer()
    value = r.get(1)

    assert default_timer() - st < 1
    assert value
