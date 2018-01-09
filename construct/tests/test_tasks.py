# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import time
from construct import Task, AsyncTask, status


def func_no_args():
    return 'SUCCESS'


def func_w_args(*args, **kwargs):
    return args, kwargs


def func_poll(interval):
    time.sleep(interval)
    return True


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
    assert r.status == status.WAITING
    assert not r.ready()
    assert r.get() == 'SUCCESS'
    assert r.ready()


def test_AsyncTask_request():
    '''Use an async task request'''

    t = AsyncTask(func_poll, 'func.poll', 'Polling task')
    r = t.request(1)

    assert r.task is t
    assert r.args == (1,)
    assert r.kwargs == {}
    assert r.status == status.WAITING
    assert not r.ready()
    assert r.get()
    assert r.ready()
