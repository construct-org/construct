# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
import os
import sys
import argparse
import colorama
import construct
from traceback import print_exception
from collections import OrderedDict
from construct import signals
from construct.constants import FAILED
from construct.cli.commands import commands, ActionCommand
from construct.cli.formatters import (
    new_formatter,
    Root,
    format_section,
    format_context
)
from construct.cli.utils import styled, style
from construct.cli.constants import (
    OPTIONS_TITLE,
    ARGUMENTS_TITLE,
    ARTIFACTS_TITLE,
    ACTION_CONTEXT_TITLE,
    STATUS_LABELS
)


@signals.route('action.before')
def on_action_before(ctx):
    print()
    print(ctx.action.description + '\n')

    if ctx.kwargs or ctx.args:
        args_data = [(k, v) for k, v in ctx.kwargs.items()]
        if ctx.args:
            args_data.append(('extra_args', ctx.args))
        args_section = format_section(
            styled('{bright}{fg.yellow}Options{reset}'),
            data=args_data,
            lcolor=style.bright
        )
        print(args_section + '\n')

    ctx_keys = ['action'] + ctx.keys
    ctx_section = format_section(
        ACTION_CONTEXT_TITLE,
        data=[(k, v) for k in ctx_keys for v in {ctx[k]} if v],
        lcolor=style.bright
    )
    print(ctx_section + '\n')


@signals.route('action.after')
def on_action_after(ctx):

    artifacts = ctx.artifacts.items()
    if not artifacts:
        print('\nNo artifacts created.')
        return

    artifacts = format_section(
        ARTIFACTS_TITLE,
        data=[(k, v) for k, v in artifacts],
        lcolor=style.bright
    )
    print('\n' + artifacts)


@signals.route('group.before')
def on_group_before(group):
    print(group.priority.description)


@signals.route('request.status.changed')
def on_request_status_change(request, last_status, status):
    msg = styled('    {bright}{:{}<50}{reset}', request.task.identifier, '.')
    msg += STATUS_LABELS[status]
    print(msg)


def logging_config(level):
    return dict(
        version=1,
        formatters={
            'simple': {
                'format': '%(levelname).1s:%(name)s> %(message)s'
            }
        },
        handlers={
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            }
        },
        loggers={
            'construct': {
                'level': level,
                'handlers': ['console'],
                'propagate': False
            }
        }
    )


def setup_parser():
    '''Build the root parser'''

    usage = styled(
        '{bright}construct '
        '{fg.blue}<command|action>{fg.reset} '
        '{fg.yellow}[options]{reset}'
    )
    parser = argparse.ArgumentParser(
        'construct',
        usage=usage,
        formatter_class=Root,
        add_help=False,
    )
    parser._optionals.title = OPTIONS_TITLE
    parser.add_argument(
        '-h',
        '--help',
        help='show this help message and exit',
        action='store_true',
        dest='-h'
    )
    parser.add_argument(
        '-v',
        '--verbose',
        help='verbose output',
        action='store_true',
        dest='-v'
    )
    parser.add_argument(
        'command',
        help=argparse.SUPPRESS,
        action='store',
        nargs='?'
    )
    return parser


def main():
    '''CLI Entry Point'''

    # Enable ansi console colors
    colorama.init()

    parser = setup_parser()
    args, extra_args = parser.parse_known_args()
    root_flags = [f for f, v in args.__dict__.items()
                  if f.startswith('-') and v]

    # Configure Construct
    logging_level = ('WARNING', 'DEBUG')[args.__dict__['-v']]
    construct.init(host='cli', logging=logging_config(logging_level))
    construct.set_context_from_path(os.getcwd())

    # Add all subcommands including contextual actions
    subcommands = OrderedDict()

    for command in commands:
        subcommands[command.name] = command(parser)

    for action in construct.actions:
        subcommands[action.identifier] = ActionCommand(action, parser)

    # Print root help if we received no command argument
    if not args.command:
        parser.print_help()
        sys.exit()

    command_name = args.command
    command_args = root_flags + extra_args

    if command_name not in subcommands:
        print('Command does not exist: ', command_name)
        sys.exit(1)

    command = subcommands[command_name]
    args, extra_args = command.parser.parse_known_args(command_args)
    args.__dict__.pop('verbose')  # We already used the verbose flag
    command.run(args, *extra_args)


if __name__ == '__main__':
    main()
