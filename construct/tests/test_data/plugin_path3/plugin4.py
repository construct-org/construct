from __future__ import absolute_import
from construct import Action
from construct.compat import basestring


class Plugin4Action(Action):

    label = 'Plugin4 Action'
    identifier = 'plugin4.action'
    parameters = {
        'argument': {
            'label': 'Argument',
            'type': basestring,
            'required': True
        }
    }
    description = 'A test action from plugin4'

    @staticmethod
    def is_available(context):
        return True


def plugin4subscriber(action):
    action.data['results'] = action.kwargs['argument']


def is_available(context):
    return True


def register(cons):
    cons.action_hub.register(Plugin4Action)


def unregister(cons):
    cons.action_hub.unregister(Plugin4Action)
