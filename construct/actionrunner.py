# -*- coding: utf-8 -*-
from __future__ import absolute_import

__all__ = ['TaskGroup', 'ActionRunner']

import logging
import six
from construct.types import Stack
from construct import signals
from construct.constants import *
from construct.errors import (
    TimeoutError,
    ValidationError,
    Abort,
    Fail,
    Pause,
    Confirm,
    Skip,
    Disable
)
from construct.tasks import AsyncRequest
from fstrings import f


_log = logging.getLogger(__name__)


class TaskGroup(object):

    def __init__(self, priority, tasks, runner):
        self.priority = priority
        self.tasks = tasks
        self.runner = runner
        self._exc = None
        self._status = WAITING

    def set_exception(self, exc):
        self.set_status(FAILED)
        self._exc = exc

    def get_exception(self):
        return self._exc

    def raise_exception(self):
        if not self._exc:
            return
        six.reraise(*self._exc)

    def set_status(self, status):
        if self._status == status:
            return
        last_status = self._status
        self._status = status
        signals.send('group.status.changed', self, last_status, status)

    def get_status(self):
        return self._status

    @property
    def waiting(self):
        return self._status == WAITING

    @property
    def running(self):
        return self._status == RUNNING

    @property
    def success(self):
        return self._status == SUCCESS

    @property
    def failed(self):
        return self._status == FAILED

    @property
    def done(self):
        return self._status in DONE_STATUSES

    def push(self):
        for task in self.tasks:
            request = self.runner._get_request(task)
            self.runner._remove_from_stacks(request)
            self.runner._waiting.push(request)

        self.set_status(PENDING)

    def reset(self):
        for task in self.tasks:
            request = self.runner._get_request(task)
            self.runner._remove_from_stacks(request)
            self.runner.ctx.requests.pop(request.task.identifier, None)

        self.set_status(WAITING)


class ActionRunner(object):

    def __init__(self, action, ctx):
        self.action = action
        self.ctx = ctx
        self._groups = {
            p: TaskGroup(p, t, self)
            for p, t in self.ctx.task_groups.items()
        }
        self._waiting = Stack()
        self._ready = Stack()
        self._failed = Stack()
        self._success = Stack()
        self._skipped = Stack()
        self._disabled = Stack()
        self._stacks = [
            self._waiting,
            self._ready,
            self._failed,
            self._success,
            self._skipped
        ]

    def _remove_from_stacks(self, request):
        for stack in self._stacks:
            try:
                stack.remove(request)
            except ValueError:
                continue

    def _fail_request(self, request):
        self._failed.push(request)
        self.ctx.results[request.task.identifier] = request._exc
        group = self._get_group(request.task.priority)
        group.set_exception(request._exc)

    def _get_group(self, priority):
        return self._groups[priority]

    def _get_request(self, task):
        '''Create a request object for a Task'''

        if task.identifier not in self.ctx.requests:
            self.ctx.requests[task.identifier] = task.request(ctx=self.ctx)

        return self.ctx.requests[task.identifier]

    def _process_waiting(self):
        '''Process waiting tasks'''

        nwaiting = len(self._waiting)
        for _ in range(nwaiting):

            request = self._waiting.pop()
            task = request.task

            if not request.enabled:
                self._disabled.push(request)

            elif task.ready(self.ctx):
                self._ready.push(request)

            elif task.skip(self.ctx):
                request.set_status(SKIPPED)
                self._skipped.push(request)

            else:
                self._waiting.push(request)

    def _process_ready(self):
        '''Process ready tasks'''

        nready = len(self._ready)
        for _ in range(nready):

            request = self._ready.pop()
            task = request.task

            if task.skip(self.ctx):
                request.set_status(SKIPPED)
                self._skipped.push(request)
                continue

            try:

                get_kwargs = {'propagate': True}
                if isinstance(request, AsyncRequest):
                    get_kwargs['timeout'] = 0

                result = request.get(**get_kwargs)

            except TimeoutError:

                # AsyncRequest timed out, push it back onto the ready stack
                # and check it again next time around
                self._ready.push(request)

            except ValidationError:

                # Task failed to validate, future tasks can handle this
                # tasks validation errors by requiring failure of this task
                # and receiving the result of this task as a parameter
                self._fail_request(request)

            except Fail:

                # Task failed but does not want to stop execution
                self._fail_request(request)

            except Abort:

                # Task explicitly sent Abort Error
                self._fail_request(request)
                raise

            except Pause:

                # Task wants to paused execution of the Action
                self._success.push(request)
                self.ctx.results[task.identifier] = result
                raise

            except Confirm:

                # Task has requested user confirmation
                self._fail_request(request)

                # TODO: Get user input on Confirm
                raise NotImplementedError(
                    'Confirm error handling not yet implemented'
                )

            except Skip:

                # Task wants to skip
                self._skipped.push(request)
                request.set_status(SKIPPED)

            except Disable:

                # Task wants to skip
                self._waiting.push(request)
                request.set_enabled(False)
                request.set_status(DISABLED)

            except Exception:

                # Propagate unrecognized exceptions
                self._fail_request(request)
                raise

            else:

                # Maybe add support for generator tasks here
                # The implementation would be a task that is a generator
                # that yields instances of other tasks
                # Each task yielded would be added to the _waiting stack
                # for future processing
                self._success.push(request)
                self.ctx.results[task.identifier] = result

            finally:

                # Perform any teardown necessary
                pass

    def _process_skipped(self):

        for _ in range(len(self._skipped)):
            request = self._skipped.pop()
            task = request.task

            if task.ready(self.ctx):
                self._ready.push(request)
            else:
                self._skipped.push(request)

    def _skip_waiting(self):

        nwaiting = len(self._waiting)
        for _ in range(nwaiting):
            request = self._waiting.pop()
            task = request.task

            if task.ready(self.ctx):
                self._ready.push(request)
            else:
                request.set_status(SKIPPED)
                self._skipped.push(request)

    def _run_once(self, propagate=True):

        while True:

            self._process_waiting()

            if not self._ready:
                self._skip_waiting()
                return

            self._process_ready()
            self._process_skipped()

    def retry_group(self, priority):
        '''Retry TaskGroup of priority'''

        group = self._get_group(priority)
        group.reset()
        self.run_group(priority)

    def run_group(self, priority):
        '''Run TaskGroup of priority'''

        group = self._get_group(priority)

        if group.waiting:

            signals.send('group.before', group)
            group.push()
            group.set_status(RUNNING)

            try:

                self._run_once()

            finally:

                if not group.failed:
                    group.set_status(SUCCESS)

                signals.send('group.after', group)

        else:

            raise Exception(f('Task Group already ran: {priority}'))

    def run(self):
        '''Run all TaskGroups of the action sequentially'''

        signals.send('action.before', self.ctx)

        try:

            for priority in self.ctx.priorities:
                self.run_group(priority)

        finally:

            signals.send('action.after', self.ctx)
