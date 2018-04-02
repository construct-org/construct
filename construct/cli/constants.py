# -*- coding: utf-8 -*-
from __future__ import absolute_import
from construct.cli.utils import styled
from collections import OrderedDict
from construct.constants import (
    WAITING,
    PENDING,
    RUNNING,
    SUCCESS,
    FAILED,
    SKIPPED,
    PAUSED,
    DISABLED,
    ENABLED,
)


ACTION_CONTEXT_TITLE = styled('{normal}Action Context{reset}')
ACTIONS_TITLE = styled('{bright}{fg.blue}Actions{reset}')
ARGUMENTS_TITLE = styled('{bright}{fg.blue}Arguments{reset}')
ARTIFACTS_TITLE = styled('{bright}{fg.green}Artifacts{reset}')
COMMANDS_TITLE = styled('{bright}{fg.blue}Commands{reset}')
CONTEXT_TITLE = styled('{normal}Current Context{reset}')
OPTIONS_TITLE = styled('{bright}{fg.yellow}Options{reset}')

TASK_TEMPLATE = '    {icon} {bright}{identifier}{sep}{reset}{description}'
TASK_ERROR_TEMPLATE = '      {bright}{fg.red}{}: {reset}{}'
STATUS_LABELS = {
    WAITING: styled('{dim}WAITING{reset}'),
    PENDING: styled('{dim}PENDING{reset}'),
    RUNNING: styled('{fg.green}RUNNING{reset}'),
    SUCCESS: styled('{bright}{fg.green}SUCCESS{reset}'),
    FAILED: styled('{bright}{fg.red}FAILED{reset}'),
    SKIPPED: styled('{fg.cyan}SKIPPED{reset}'),
    PAUSED: styled('{fg.red}PAUSED{reset}'),
    DISABLED: styled('{dim}DISABLED{reset}'),
    ENABLED: styled('{bright}ENABLED{reset}'),
}
ICONS = OrderedDict([
    ('ENABLED', styled('{dim}{fg.green}◌{reset}')),
    ('DISABLED', styled('{dim}{fg.red}◌{reset}')),
    ('WAITING', styled('{dim}◌{reset}')),
    ('RUNNING', styled('{fg.green}◌{reset}')),
    ('PENDING', styled('{bright}{fg.magenta}◌{reset}')),
    ('PAUSED', styled('{bright}{fg.cyan}◌{reset}')),
    ('SKIPPED', styled('{bright}{fg.blue}◌{reset}')),
    ('SUCCESS', styled('{bright}{fg.green}●{reset}')),
    ('FAILED', styled('{bright}{fg.red}●{reset}')),
])
