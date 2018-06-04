# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import time
from timeit import default_timer
from construct.tasks import Task, AsyncTask, task, TaskCollection
from construct.errors import TimeoutError
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


def test_task_decorator():
    '''Task function decorator'''

    @task
    def null_task():
        return True

    assert not null_task.bound
    assert null_task.identifier == 'null_task'
    assert null_task.priority == 0
    assert null_task()
    assert null_task.ready(None)

    r = null_task.request()
    assert r.get()


def test_task_method():
    '''Task method decorator'''

    class ObjectWithTasks(object):

        @task(priority=0)
        def task_a(self):
            return True

    tc = ObjectWithTasks()

    assert tc.task_a is tc.task_a
    assert tc.task_a.bound
    assert tc.task_a.identifier == 'task_a'
    assert tc.task_a()

    tc2 = ObjectWithTasks()

    assert tc.task_a is not tc2.task_a


@task
def null_task():
    return True


class TestCollection(TaskCollection):

    identifier = 'test_collection'

    @task(priority=0)
    def task_a(self):
        return True

    @task(priority=1)
    def task_b(self):
        return False

    @task(priority=2)
    def task_c(self):
        return False


def test_task_collection_methods():
    '''TaskCollection automagical task registration'''

    tc = TestCollection()

    # Membership tests use task identifiers
    assert TestCollection.task_a in tc
    assert TestCollection.task_b in tc
    assert TestCollection.task_c in tc
    assert tc.task_a()
    assert not tc.task_b()
    assert not tc.task_c()

    # All task methods are automagically bound in __init__
    assert tc.task_a.bound and tc.task_a.parent is tc
    assert tc.task_b.bound and tc.task_b.parent is tc
    assert tc.task_c.bound and tc.task_c.parent is tc
    assert len(tc) == 3


def test_task_collection_add_remove():
    '''TaskCollection append and remove'''

    tc = TestCollection()

    # Add a task
    tc.append(null_task)
    assert null_task in tc
    assert len(tc) == 4
    assert hasattr(tc, null_task.func_name)
    assert tc.null_task()

    # Does nothing
    tc.append(null_task)
    assert len(tc) == 4

    # Remove a task
    tc.remove(null_task)
    assert null_task not in tc
    assert len(tc) == 3
    assert not hasattr(tc, null_task.func_name)

    # Does nothing
    tc.remove(null_task)
    assert len(tc) == 3


def test_task_collection_init_args():
    '''TaskCollection init args'''

    @task(priority=0)
    def task_a():
        return True

    @task(priority=1)
    def task_b():
        return False

    @task(priority=2)
    def task_c():
        return False

    tc = TaskCollection('identifier', [task_a, task_b, task_c])
    assert tc.identifier == 'identifier'
    assert len(tc) == 3
    assert tc.task_a()
    assert not tc.task_b()
    assert not tc.task_c()

    tc.remove(task_a)
    tc.remove(task_b)
    tc.remove(task_c)
    assert len(tc) == 0
    assert not hasattr(tc, task_a.func_name)
    assert not hasattr(tc, task_b.func_name)
    assert not hasattr(tc, task_c.func_name)
