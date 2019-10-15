# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

# Standard library imports
import argparse
import logging
import os
import sys
import traceback
from textwrap import dedent

# Third party imports
from scrim import get_scrim

# Local imports
import construct

# Local imports
from ..utils import classproperty
from .constants import ARGUMENTS_TITLE, OPTIONS_TITLE
from .formatters import Contextual, format_section, new_formatter
from .utils import abort, error, styled


_log = logging.getLogger(__name__)


class Command(object):
    '''Base class for all CLI Commands. Override :meth:`setup_parser` to add
    arguments to a command. Implement :meth:`run` to customize what happens
    when the command is invoked.
    '''

    name = None

    def __init__(self, parent):
        self.parent = parent
        self.parser = argparse.ArgumentParser(
            self.name,
            formatter_class=new_formatter(self, Contextual)
        )
        self.parser._optionals.title = OPTIONS_TITLE
        self.parser._positionals.title = ARGUMENTS_TITLE
        self.parser.add_argument(
            '-v',
            '--verbose',
            help='verbose output',
            action='store_true',
        )
        self._parser_setup = False

    @classmethod
    def _available(cls):
        return cls.name and cls.available()

    @classmethod
    def available(cls):
        '''Implement this to set when a command is available.'''
        return True

    @property
    def arguments(self):
        return self.parser._get_positional_actions()

    @property
    def options(self):
        return self.parser._get_optional_actions()

    @property
    def usage(self):
        usage = styled('{bright}{} {}', self.parent.prog, self.name)
        for argument in self.arguments:
            usage += styled(' {fg.blue}<{}>', argument.dest)
        if self.options:
            usage += styled(' {fg.yellow}[options]')
        usage += styled('{reset}')
        return usage

    @classproperty
    def short_description(cls):
        return cls.__doc__.split('\n')[0]

    @classproperty
    def description(cls):
        parts = cls.__doc__.split('\n')
        short = parts[0]
        body = dedent('\n'.join(parts[1:]))
        text = '\n'.join([short, body])
        return text

    def _setup_parser(self, parser):
        if not self._parser_setup:
            self.setup_parser(self.parser)
        self._parser_setup = True

    def setup_parser(self, parser):
        return NotImplemented

    def parse(self, args):
        self._setup_parser(self.parser)
        args, extra_args = self.parser.parse_known_args(args)
        return args, extra_args

    def run(self, args, *extra_args):
        return NotImplemented


class Version(Command):
    '''Version information'''

    name = 'version'

    def run(self, args, *extra_args):
        section = format_section(
            '',
            [
                ('', ''),
                ('name', construct.__title__),
                ('version', construct.__version__),
                ('url', construct.__url__),
                ('package', os.path.dirname(construct.__file__)),
                ('config', os.environ.get('CONSTRUCT_CONFIG', 'default')),
            ],
            lcolor=styled('{bright}')
        )
        print(section)


def requires_scrim(command):
    '''Command becomes available only when cli run by scrim script...

    See also:
        https://github.com/danbradham/scrim
    '''

    command.available = staticmethod(lambda: get_scrim().shell)
    return command


@requires_scrim
class Home(Command):
    '''Go to root directory'''

    name = 'home'

    def run(self, args, *extra_args):
        ctx = construct.get_context()

        if not os.path.exists(ctx.root):
            os.makedirs(ctx.root)

        scrim = get_scrim()
        scrim.pushd(ctx.root)


@requires_scrim
class Pop(Command):
    '''Go back to last location'''

    name = 'pop'

    def run(self, args, *extra_args):
        scrim = get_scrim()
        scrim.popd()


@requires_scrim
class Push(Command):
    '''Go to first search result'''

    name = 'push'

    def setup_parser(self, parser):
        parser.add_argument(
            'name',
            nargs='?',
            help='Name of Entry like: my_project or my_project/my_asset',
        )
        parser.add_argument(
            '-r', '--root',
            default=os.getcwd(),
            help='Root directory of search',
            type=str,
        )
        parser.add_argument(
            '--up',
            action='store_true',
            default=False,
            help='Search up tree instead of down',
            dest='direction'
        )
        parser.add_argument(
            '-t', '--tags',
            nargs='*',
            help='List of tags like: project'
        )
        parser.add_argument(
            '-d', '--depth',
            type=int,
            required=False,
            help='Search depth'
        )

    def run(self, args, *extra_args):

        import fsfs
        api = construct.API()
        ctx = api.context.copy()

        if not args.tags and args.name:
            query = dict(
                selector=args.name,
                root=args.root,
                skip_root=True
            )
            entry = fsfs.quick_select(**query)
        else:
            query = dict(
                root=args.root,
                name=args.name,
                tags=args.tags,
                direction=args.direction,
                depth=args.depth or (3 if ctx.project else 2),
                skip_root=True
            )
            # Get a better match, not just the first hit
            entries = list(fsfs.search(**query))

            if not entries:
                error('Could not find entry...')
                sys.exit(1)

            if len(entries) == 1:
                entry = entries[0]
            else:
                # The shortest entry has to be the closest to our query
                entry = min(entries, key=lambda e: len(e.path))

        if not entry:
            error('Could not find entry...')
            sys.exit(1)

        path = entry.path
        if args.name:
            parts = args.name.split('/')
            for part in parts:
                highlight = styled('{bright}{fg.yellow}{}{reset}', part)
                path = path.replace(part, highlight)
        print(path)

        scrim = get_scrim()
        scrim.pushd(os.path.abspath(entry.path))


class Search(Command):
    '''Search for Entries

    Examples:
      construct search my_project
      construct search my_project/my_asset
      construct search -t asset
      construct search -t workspace maya
    '''

    name = 'search'

    def setup_parser(self, parser):
        parser.add_argument(
            'name',
            nargs='?',
            help='Name of Entry',
        )
        parser.add_argument(
            '-r', '--root',
            default=os.getcwd(),
            help='Root directory of search',
            type=str,
        )
        parser.add_argument(
            '--up',
            action='store_true',
            default=False,
            help='Search up tree instead of down',
            dest='direction'
        )
        parser.add_argument(
            '-t', '--tags',
            nargs='*',
            help='List of tags like: project'
        )
        parser.add_argument(
            '-d', '--depth',
            type=int,
            required=False,
            help='Search depth'
        )

    def run(self, args, *extra_args):
        api = construct.API()
        ctx = api.context.copy()
        query = dict(
            root=args.root,
            name=args.name,
            tags=args.tags,
            direction=args.direction,
            depth=args.depth or (3 if ctx.project else 1),
        )
        entries = construct.search(**query)

        i = 0
        for i, entry in enumerate(entries):
            path = entry.path
            if args.name:
                parts = args.name.split('/')
                for part in parts:
                    highlight = styled('{bright}{fg.yellow}{}{reset}', part)
                    path = path.replace(part, highlight)
            print(path)

        if i == 0:
            print(('Found 0 result.'))


class Read(Command):
    '''Read metadata'''

    name = 'read'

    def setup_parser(self, parser):
        parser.add_argument(
            '--root', '-r',
            default=os.getcwd(),
            help='Directory to read from'
        )
        parser.add_argument('keys', nargs=-1, help='keys to read')

    def run(self, args, *extra_args):
        import fsfs
        data = fsfs.read(args.root, *args.keys)
        print(fsfs.encode_data(data))


class Write(Command):
    '''Write metadata'''

    name = 'write'

    def setup_parser(self, parser):
        parser.add_argument(
            '--root', '-r',
            default=os.getcwd(),
            help='Directory to read from'
        )
        parser.add_argument(
            '-k', '--key',
            dest='data',
            required=True,
            action='append',
            nargs=2,
            help='key value pairs to write'
        )
        parser.add_argument(
            '-d', '--delete',
            dest='delkeys',
            action='append',
            help='Keys to delete',
            nargs=1
        )

    def run(self, args, *extra_args):

        import fsfs
        from fsfs.cli import safe_eval

        entry = fsfs.get_entry(args.root)
        if args.delkeys:
            entry.remove(*args.delkeys)

        data = {k: safe_eval(v) for k, v in args.data}

        try:
            entry.write(**data)
        except Exception as e:
            print('Failed to write data: ')
            print(dict(data))
            print(e.message)
        else:
            print('Wrote data to ' + args.root)


class Tag(Command):
    '''Tag a directory

    Examples:
        construct tag project
        construct tag task model

    Unless you know what you're doing, don't add tags.
    '''

    name = 'tag'

    def setup_parser(self, parser):
        parser.add_argument(
            '--root', '-r',
            default=os.getcwd(),
            help='Directory to tag'
        )
        parser.add_argument('tags', nargs='*', help='List of tags to add')

    def run(self, args, *extra_args):
        import fsfs
        fsfs.tag(args.root, *args.tags)


class Untag(Command):
    '''Untag a directory

    Examples:
        construct untag project
        construct untag task model

    Unless you know what you're doing, don't remove tags.
    '''

    name = 'untag'

    def setup_parser(self, parser):
        parser.add_argument(
            '--root', '-r',
            default=os.getcwd(),
            help='Directory to tag'
        )
        parser.add_argument('tags', nargs='*', help='List of tags to remove')

    def run(self, args, *extra_args):
        import fsfs
        fsfs.untag(args.root, *args.tags)


class ActionCommand(Command):
    ''':class:`Action` CLI command class'''

    def __init__(self, action, parent):
        _log.debug('Initializing ActionCommand for %s' % action.identifier)
        self.action = action
        self.name = action.identifier
        super(ActionCommand, self).__init__(parent)

    @property
    def short_description(self):
        return self.action.short_description

    @property
    def description(self):
        return self.action.description

    def custom_validator(self, name, cast, *validators):
        def check_value(value):
            value = cast(value)
            if not all([v(value) for v in validators]):
                msg = '%s: invalid value: %r' % (name, value)
                raise abort(msg)
            return value
        return check_value

    def add_option(self, parser, param_name, param_options):
        '''Add an argument to parser from an action parameter'''
        param_flag = '--' + param_name

        # Handle bool options
        if param_options['type'] is bool:
            arg_spec = dict(
                action='store_true',
                dest=param_name,
                help=param_options.get('help', None),
                default=param_options.get('default', False),
            )
            return parser.add_argument(param_flag, **arg_spec)

        # Handle all other options
        arg_spec = dict(
            action=('store', 'store_true')[param_options['type'] is bool],
            type=param_options.get('type', str),
            dest=param_name,
            help=param_options.get('help', None),
            # required=param_options.get('required', False),
            default=param_options.get('default', None),
            choices=param_options.get('options', None)
        )

        # Build a validator if we get a tuple of types, argparse calls
        # type(arg), so our validator casts the argument first, then
        # validates it.
        cast = arg_spec['type']
        validators = param_options.get('validator', [])
        if isinstance(param_options['type'], tuple):
            cast = param_options['type'][0]
            validators.append(lambda x: isinstance(x, param_options['type']))

        if validators:
            arg_spec['type'] = self.custom_validator(
                param_flag,
                cast,
                *validators
            )

        parser.add_argument(param_flag, **arg_spec)

    def setup_parser(self, parser):
        api = construct.API()
        ctx = api.context.copy()
        params = self.action.params(ctx)
        for param_name, param_options in params.items():
            self.add_option(parser, param_name, param_options)

    def run(self, args, *extra_args):
        try:
            action = self.action(*extra_args, **args.__dict__)
            action.run()
        except ActionControlFlowError as e:
            msg = styled(
                '{bright}{fg.red}Control Flow Error:{fg.reset} {}'
                ' raised critical error {fg.red}{}{reset}',
                self.action.identifier,
                e.__class__.__name__
            )
            print(msg)
        except ArgumentError as e:
            msg = styled('{bright}{fg.red}Argument Error:{fg.reset} {}', e)
            print(msg)
        except Exception as e:
            msg = styled(
                '{bright}{fg.red}Action Error:{fg.reset} {}'
                ' raised unexpected error {fg.red}{}{reset}\n',
                self.action.identifier,
                e.__class__.__name__
            )
            print(msg)
            traceback.print_exc()


commands = [c for c in Command.__subclasses__() if c._available()]
