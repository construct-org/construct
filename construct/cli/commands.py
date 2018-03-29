# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
import argparse
import os
import sys
from textwrap import dedent
from scrim import get_scrim
import logging
import construct
from construct.errors import ActionControlFlowError
from construct.cli.formatters import new_formatter, Contextual, format_section
from construct.cli.constants import OPTIONS_TITLE, ARGUMENTS_TITLE
from construct.cli.utils import styled, error, abort


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
        self.setup_parser(self.parser)

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

    @property
    def description(self):
        parts = self.__doc__.split('\n')
        short = parts[0]
        body = dedent('\n'.join(parts[1:]))
        text = '\n'.join([short, body])
        return text

    def setup_parser(self, parser):
        return NotImplemented

    def run(self, args):
        return NotImplemented


class Version(Command):
    '''Version information'''

    name = 'version'

    def run(self, args):
        section = format_section(
            '',
            [
                ('', ''),
                ('name', construct.__title__),
                ('version', construct.__version__),
                ('url', construct.__url__)
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

    def run(self, args):
        ctx = construct.get_context()
        scrim = get_scrim()
        scrim.pushd(os.path.abspath(ctx.root))


@requires_scrim
class Pop(Command):
    '''Go back to last location'''

    name = 'pop'

    def run(self, args):
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

    def run(self, args):
        ctx = construct.get_context()
        query = dict(
            root=args.root,
            name=args.name,
            tags=args.tags,
            direction=args.direction
        )
        entry = construct.search(**query).one()

        if not entry:
            error('Could not find entry for query...')
            sys.exit(1)

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

    def run(self, args):
        ctx = construct.get_context()
        query = dict(
            root=args.root,
            name=args.name,
            tags=args.tags,
            direction=args.direction
        )
        entries = list(construct.search(**query))

        if not entries:
            print(('Found 0 result.'))
            sys.exit(1)

        for entry in entries:
            # TODO: Highlight parts of path matching query
            print(entry)


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

    def run(self, args):
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

    def run(self, args):

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

    def run(self, args):
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

    def run(self, args):
        import fsfs
        fsfs.untag(args.root, *args.tags)


class ActionCommand(Command):
    ''':class:`Action` CLI command class'''

    def __init__(self, action, parent):
        _log.debug('Initializing ActionCommand for %s' % self.name)
        self.action = action
        self.name = action.identifier
        super(ActionCommand, self).__init__(parent)

    @property
    def description(self):
        parts = self.action.description.split('\n')
        text = '\n'.join([parts[0], dedent('\n'.join(parts[1:]))])
        return text

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
            required=param_options.get('required', False),
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
        ctx = construct.get_context()
        params = self.action.params(ctx)
        for param_name, param_options in params.items():
            self.add_option(parser, param_name, param_options)

    def run(self, args):
        print(args)
        try:
            action = self.action(**args.__dict__)
            action.run()
        except ActionControlFlowError as e:
            print(styled('{fg.red}{}{reset}', e.message))


commands = [c for c in Command.__subclasses__() if c._available()]
