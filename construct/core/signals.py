# -*- coding: utf-8 -*-
from construct.cote.signal import SignalRouter

router = SignalRouter()

# Migrate to new signals
get_context = router.signal('get.context')
action_before = router.signal('action.before')
action_after = router.signal('action.after')
action_success = router.signal('action.success')
action_failure = router.signal('action.failure')
action_skipped = router.signal('action.skipped')
action_group_before = router.signal('action.group.before')
action_group_after = router.signal('action.group.after')
action_group_success = router.signal('action.group.success')
action_group_failure = router.signal('action.group.failure')
action_group_skipped = router.signal('action.group.skipped')
action_task_before = router.signal('action.task.before')
action_task_after = router.signal('action.task.after')
action_task_success = router.signal('action.task.success')
action_task_failure = router.signal('action.task.failure')
action_task_skipped = router.signal('action.task.skipped')
