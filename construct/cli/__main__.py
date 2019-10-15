# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

# Standard library imports
import argparse
import sys
from collections import OrderedDict

# Third party imports
import colorama
import win_unicode_console

# Local imports
from .. import API
from .commands import commands
from .constants import OPTIONS_TITLE
from .formatters import Root
from .utils import styled


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
    win_unicode_console.enable()
    colorama.init()

    parser = setup_parser()
    args, extra_args = parser.parse_known_args()
    root_flags = [f for f, v in args.__dict__.items()
                  if f.startswith('-') and v]

    # Configure Construct
    logging_level = ('WARNING', 'DEBUG')[args.__dict__['-v']]
    api = API(logging=logging_config(logging_level))
    api.context['host'] = 'cli'
    # api.set_context_from_path(os.getcwd())

    # Add all subcommands including contextual actions
    subcommands = OrderedDict()

    for command in commands:
        subcommands[command.name] = command(parser)

    # for action in construct.actions:
    #     subcommands[action.identifier] = ActionCommand(action, parser)

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
    args, extra_args = command.parse(command_args)
    args.__dict__.pop('verbose')
    command.run(args, *extra_args)


if __name__ == '__main__':
    main()
