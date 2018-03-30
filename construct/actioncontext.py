# -*- coding: utf-8 -*-
from __future__ import absolute_import
from collections import OrderedDict
from construct.context import Context
from construct.tasks import group_tasks
from construct import types, actionparams
from construct.constants import WAITING


class ActionContext(Context):

    def __init__(self, action, args, kwargs, ctx=None):
        from construct.api import actions, get_context

        if ctx is None:
            ctx = get_context()
        super(ActionContext, self).__init__(**ctx.__dict__)

        self.action = action
        self.status = WAITING
        self.tasks = actions.collect_tasks(action, self)
        self.task_groups = group_tasks(self.tasks)
        self.priorities = list(self.task_groups.keys())
        self.results = {t.identifier: None for t in self.tasks}
        self.requests = {}
        self.artifacts = types.Namespace()
        self.store = types.Namespace()
        self.args = args
        self.kwargs = actionparams.get_defaults(action.params(ctx))
        self.kwargs.update(kwargs)
