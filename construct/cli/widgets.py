# -*- coding: utf-8 -*-
from __future__ import absolute_import, division
from construct.cli.stout import Line
from construct.cli.constants import (
    STATUS_LABELS,
    ICONS
)
from construct.cli.utils import styled, style
from construct.constants import WAITING, FAILED
from construct import signals


class TaskLine(Line):

    template = '    {icon} {bright}{identifier}{sep}{reset}{description}'
    error_template = '      {bright}{fg.red}{}: {reset}{}'

    def __init__(self, task, console):
        self.task = task
        self.status = WAITING
        text = self.format_status(self.status)
        super(TaskLine, self).__init__(text, console)

    def format_error(self, exc_info):
        # Insert error message
        exc_type, exc_value, exc_tb = exc_info
        err = styled(self.error_template, exc_type.__name__, exc_value)
        return err

    def format_status(self, status):
        return styled(
            self.template,
            icon=ICONS[self.status],
            identifier=self.task.identifier + style.reset,
            description=self.task.description,
            sep=' - '
        )

    def set_status(self, status):
        self.status = status
        self.text = self.format_status(status)


class ProgressBar(Line):

    info_template = '{label} <{i} of {max}> '
    bar_template = '{bright}{color}{lfill}{dim}{rfill}{reset}'
    lfill_char = '░'
    rfill_char = '░'
    color_map = [
        style.fg.red,
        style.fg.yellow,
        style.fg.green
    ]

    def __init__(self, label, max, console):
        self.label = label
        self.max = max
        self.width = min(76, console.width - 2)
        self.i = 0
        text = self.format_bar()
        super(ProgressBar, self).__init__(text, console)

    def get_color(self, percent):
        from math import floor
        index = int(floor(percent * (len(self.color_map) - 1)))
        return self.color_map[index]

    def format_bar(self):
        info = self.info_template.format(
            label=self.label,
            i=self.i,
            max=self.max
        )
        info_width = len(info)
        bar_width = self.width - info_width
        if self.i == 0:
            percent = 0
        else:
            percent = self.i / self.max

        lfill_width = int(bar_width * percent)
        rfill_width = bar_width - lfill_width
        return styled(
            info + self.bar_template,
            color=self.get_color(percent),
            lfill=self.lfill_char * lfill_width,
            rfill=self.rfill_char * rfill_width
        )

    def set_value(self, i):
        self.i = i
        self.text = self.format_bar()
