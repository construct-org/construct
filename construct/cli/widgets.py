# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sys
from construct.cli.stout import Line
from construct.cli.constants import (
    TASK_ERROR_TEMPLATE,
    TASK_TEMPLATE,
    STATUS_LABELS,
    ICONS
)
from construct.cli.utils import styled, style
from construct.constants import WAITING, FAILED
from construct import signals


class TaskLine(Line):

    def __init__(self, task, console):
        self.task = task
        self.status = WAITING
        text = self.format_status(self.status)
        super(TaskLine, self).__init__(text, console)

    def format_error(self, exc_info):
        # Insert error message
        exc_type, exc_value, exc_tb = exc_info
        err = styled(TASK_ERROR_TEMPLATE, exc_type.__name__, exc_value)
        return err

    def format_status(self, status):
        return styled(
            TASK_TEMPLATE,
            icon=ICONS[self.status],
            identifier=self.task.identifier + style.reset,
            status= '',
            sep=''
        )

    def set_status(self, status):
        self.status = status
        self.text = self.format_status(status)
