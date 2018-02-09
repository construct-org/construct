# -*- coding: utf-8 -*-
from nose.tools import raises
from construct.constants import *
from construct.err import RegistrationError
from construct.actionhub import ActionHub
from construct.action import Action
from construct.tasks import task


class GenericAction(Action):

    label = 'Generic Action'
    identifier = 'generic.action'
    description = 'Generic Action accepts no parameters'
    parameters = {}

    @staticmethod
    def available(ctx):
        return True


@task
def generic_task():
    return True


def test_action_registration():
    '''ActionHub.un/register'''

    hub = ActionHub()
    hub.register(GenericAction)
    assert GenericAction.identifier in hub.get_actions()

    hub.unregister(GenericAction)
    assert GenericAction.identifier not in hub.get_actions()


@raises(RegistrationError)
def test_action_register_twice():
    '''ActionHub.register again raises'''

    hub = ActionHub()
    hub.register(GenericAction)
    hub.register(GenericAction)


@raises(TypeError)
def test_action_register_wrong_type():
    '''ActionHub.register wrong type raises'''

    hub = ActionHub()
    hub.register('thing')


def test_task_connect():
    '''ActionHub.dis/connect'''

    hub = ActionHub()
    hub.connect('generic.action', generic_task)
    assert generic_task in hub.get_tasks('generic.action')

    hub.connect('generic.action', generic_task)
    assert len(hub.get_tasks('generic.action')) == 1

    hub.disconnect('generic.action', generic_task)
    assert generic_task not in hub.get_tasks('generic.action')


def test_clear():
    '''ActionHub.clear'''

    class GenericActionB(GenericAction):
        identifier = 'generic.action.b'

    hub = ActionHub()
    hub.register(GenericAction)
    hub.register(GenericActionB)
    hub.connect('generic.action', generic_task)
    hub.connect('generic.action.b', generic_task)

    hub.clear('generic.action')
    assert not hub.get_tasks('generic.action')
    assert hub.get_tasks('generic.action.b')

    hub.clear()
    assert not hub.get_actions()
    assert not hub.get_tasks('generic.action.b')


def test_action_creation():
    '''ActionHub.__call__ GenericAction'''

    hub = ActionHub()
    generic_action = hub.register(GenericAction)
    generic_action.connect(generic_task)

    action = generic_action()
    assert generic_task in action.tasks
    assert not action.requests
    assert action.status == WAITING

    action.run()
    assert action.results[generic_task.identifier]
