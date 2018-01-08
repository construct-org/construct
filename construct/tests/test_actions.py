'''
Test ActionHub and Actions
==========================
'''

from __future__ import absolute_import, print_function
import shutil
import tempfile
from construct import Construct, Action
from construct.tests import data_path


def test_register_action():
    '''Create and register an action'''

    class BaseAction(Action):

        label = 'Base Action'
        identifier = 'base.action'
        description = 'Base action description'
        parameters = {
            'message': {
                'type': str,
                'label': 'Message',
            }
        }

        @staticmethod
        def is_available(context):
            return True

    def first(action):
        return 1

    def second(action):
        return 2

    cons = Construct()
    cons.action_hub.register(BaseAction)
    cons.action_hub.subscribe('base.action', first, priority=0)
    cons.action_hub.subscribe('base.action', second, priority=1)
    action = cons.action_hub.run('base.action', message='Hello World!')

    assert action.done
    assert not action.running
    assert action.exc is None
    assert action.results['first'].value == 1
    assert action.results['second'].value == 2
    assert action.step is None
    assert action.step_index == -1


def test_plugin_subscribes():
    '''Plugin subscribes to Constuct default actions'''

    temp = tempfile.mkdtemp()
    cons = Construct(plugin_paths=[
        data_path('plugin_actions')
    ])

    assert 'default_actions' in cons.plugins
    assert cons.plugins['default_actions'].enabled

    action = cons.new_project(root=temp + '/project')
    assert action.data['capture'] == ['new.project']

    shutil.rmtree(temp)


def test_action_iterate():
    '''Send action in priority groups.'''

    cons = Construct()

    class MultiStageAction(Action):

        label = 'Multi Stage Action'
        identifier = 'multi.action'
        description = 'Action with multiple subscribers with diff priorities'

        @staticmethod
        def is_available(context):
            return True

    def make_subscriber(index):
        name = 'subscriber' + str(index)

        def subscriber(action):
            return name
        subscriber.func_name = name
        return subscriber

    cons.action_hub.register(MultiStageAction)

    for priority in range(4):
        for i in range(4):
            index = priority * 4 + i
            cons.action_hub.subscribe(
                'multi.action',
                make_subscriber(index),
                priority=priority
            )

    action = cons.action_hub.new_action('multi.action')
    for priority, group in action:
        action.run_group(priority, group, continue_on_error=False)

    assert len(action.results) == 16
