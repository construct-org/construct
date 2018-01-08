# -*- coding: utf-8 -*-
from construct.cote.signal import SignalHub

hub = SignalHub()

action_init = hub.signal('action.init')
action_ready = hub.signal('action.ready')
action_done = hub.signal('action.done')
action_error = hub.signal('action.error')
action_step_ready = hub.signal('action.step_ready')
action_step_done = hub.signal('action.step_done')
action_group_ready = hub.signal('action.group_ready')
action_group_done = hub.signal('action.group_done')

# Migrate to new signals
get_context = hub.signal('get.context')
action_before = hub.signal('action.before')
action_after = hub.signal('action.after')
action_success = hub.signal('action.success')
action_failure = hub.signal('action.failure')
action_skipped = hub.signal('action.skipped')
action_group_before = hub.signal('action.group.before')
action_group_after = hub.signal('action.group.after')
action_group_success = hub.signal('action.group.success')
action_group_failure = hub.signal('action.group.failure')
action_group_skipped = hub.signal('action.group.skipped')
action_task_before = hub.signal('action.task.before')
action_task_after = hub.signal('action.task.after')
action_task_success = hub.signal('action.task.success')
action_task_failure = hub.signal('action.task.failure')
action_task_skipped = hub.signal('action.task.skipped')
