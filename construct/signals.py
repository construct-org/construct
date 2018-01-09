# -*- coding: utf-8 -*-
from __future__ import absolute_import
from construct.core.signal import SignalHub

_signals = SignalHub()

action_before = _signals.signal('action.before')
action_after = _signals.signal('action.after')
action_success = _signals.signal('action.success')
action_failure = _signals.signal('action.failure')
action_skipped = _signals.signal('action.skipped')
action_group_before = _signals.signal('action.group.before')
action_group_after = _signals.signal('action.group.after')
action_group_success = _signals.signal('action.group.success')
action_group_failure = _signals.signal('action.group.failure')
action_group_skipped = _signals.signal('action.group.skipped')
action_task_before = _signals.signal('action.task.before')
action_task_after = _signals.signal('action.task.after')
action_task_success = _signals.signal('action.task.success')
action_task_failure = _signals.signal('action.task.failure')
action_task_skipped = _signals.signal('action.task.skipped')
