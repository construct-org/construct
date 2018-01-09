# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function


def capture_action(action):

    capture = action.data.setdefault('capture', [])
    capture.append(action.identifier)


def available(context):
    return True


def register(cons):

    cons.new_project.subscribe(capture_action)
    cons.new_asset.subscribe(capture_action)
    cons.new_task.subscribe(capture_action)
    cons.new_sequence.subscribe(capture_action)
    cons.new_shot.subscribe(capture_action)
    cons.new_workspace.subscribe(capture_action)


def unregister(cons):

    cons.new_project.unsubscribe(capture_action)
    cons.new_asset.unsubscribe(capture_action)
    cons.new_task.unsubscribe(capture_action)
    cons.new_sequence.unsubscribe(capture_action)
    cons.new_shot.unsubscribe(capture_action)
    cons.new_workspace.unsubscribe(capture_action)
