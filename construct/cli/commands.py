# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
import argparse
import os
import sys
from textwrap import dedent
from scrim import get_scrim
import construct
from construct.cli.formatters import new_formatter, Contextual, format_section
from construct.cli.constants import OPTIONS_TITLE, ARGUMENTS_TITLE
from construct.cli.utils import styled, error, abort


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
        return cls.name is not None

    @staticmethod
    def available():
        True

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
        text = '\n'.join([parts[0], body])
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


class ScrimCommand(Command):
    '''Commands only available when scrim is enabled

    see also:
        https://github.com/danbradham/scrim
    '''

    @staticmethod
    def available():
        return get_scrim().path is not None


class Home(ScrimCommand):
    '''Go to root directory'''

    name = 'home'

    def run(self, args):
        ctx = construct.get_context()
        scrim = get_scrim()
        scrim.pushd(os.path.abspath(ctx.root))
        print(scrim.to_cmd())


class Pop(ScrimCommand):
    '''Go back to last location'''

    name = 'pop'

    def run(self, args):
        scrim = get_scrim()
        scrim.popd()
        print(scrim.to_cmd())


class Push(ScrimCommand):
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
        entry = construct.one(**query)

        if not entry:
            error('Could not find entry for query...')
            sys.exit(1)

        scrim = get_scrim()
        scrim.pushd(os.path.abspath(entry.path))
        print(scrim.to_cmd())


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
            print('Found 0 result.')
            sys.exit(1)

        for entry in entries:
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
        data = fsfs.read(root, *keys)
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
        from fsfs.cli import literal_eval

        entry = fsfs.get_entry(root)
        if args.delkeys:
            entry.remove(*args.delkeys)

        data = {k: literal_eval(v) for k, v in args.data}

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
        parser.add_argument('tags', nargs=-1, help='List of tags to add')

    def run(self, args):
        import fsfs
        fsfs.untag(args.root, *args.tags)


class ActionCommand(Command):
    ''':class:`Action` CLI command class'''

    def __init__(self, action, parent):
        self.action = action
        self.name = action.identifier
        super(ActionCommand, self).__init__(parent)

    @property
    def description(self):
        parts = self.action.description.split('\n')
        text = '\n'.join([parts[0], dedent('\n'.join(parts[1:]))])
        return text

    def custom_validator(self, name, type, validator):
        def check_value(value):
            value = type(value)
            if not validator(value):
                msg = '%s: invalid value: %r' % (name, value)
                raise self.parser.error(msg)
            return value
        return check_value

    def add_option(self, parser, param_name, param_options):
        '''Add an argument to parser from an action parameter'''
        param_flag = '--' + param_name
        data = {
            'dest': param_name,
            'type': param_options['type'],
            'help': param_options['help'],
            'required': param_options.get('required', False)
        }
        if param_options['type'] is bool:
            data['action'] = 'store_true'
        else:
            data['action'] = 'store'

        if 'validator' in param_options:
            data['type'] = self.custom_validator(
                param_flag,
                param_options['type'],
                param_options['validator']
            )

        if 'default' in param_options:
            data['default'] = param_options['default']

        if 'options' in param_options:
            data['choices'] = param_options['options']

        parser.add_argument(param_flag, **data)

    def setup_parser(self, parser):
        ctx = construct.get_context()
        params = self.action.params(ctx)
        for param_name, param_options in params.items():
            self.add_option(parser, param_name, param_options)

    def run(self, args):
        try:
            action = self.action(**args.__dict__)
            action.run()
        except ActionControlFlowError as e:
            print(styled('{fg.red}{}{reset}', e.message))

commands = [c for c in Command.__subclasses__() if c._available()]
