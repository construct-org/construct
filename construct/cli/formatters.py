# -*- coding: utf-8 -*-
from __future__ import absolute_import

# Standard library imports
import argparse

# Local imports
import construct
from construct.cli.constants import (
    ACTIONS_TITLE,
    COMMANDS_TITLE,
    CONTEXT_TITLE,
)

# Local imports
from .utils import style, styled


reset = style.reset


def new_formatter(parent, formatter_type):
    return type(
        formatter_type.__name__,
        (formatter_type,),
        dict(
            parent=parent
        )
    )


def format_context():
    api = construct.API()
    ctx = api.context.copy()
    ctx_data = []
    for k in ctx._keys:
        v = ctx[k]
        if not v:
            continue
        try:
            ctx_data.append((k, v['name']))
        except (KeyError, TypeError):
            ctx_data.append((k, v))
    return format_section(
        CONTEXT_TITLE,
        ctx_data,
        lcolor=styled('{bright}')
    )


def format_commands():
    from construct.cli.commands import commands
    return format_section(
        COMMANDS_TITLE,
        [(c.name, c.short_description) for c in commands],
        lcolor=styled('{bright}')
    )


def format_actions():
    api = construct.API()
    actions = api.actions.get_available()
    return format_section(
        ACTIONS_TITLE,
        [(a.identifier, a.description) for a in actions],
        lcolor=styled('{bright}')
    )


def format_section(title, data, indent='', lcolor=reset, rcolor=reset):
    '''Format a section'''

    if isinstance(data, dict):
        data = list(data.items())

    width = max(max([len(k) for k, v in data]), 12)
    line = indent + '  {lc}{:<{w}}{reset}  {rc}{}{reset}'

    lines = []
    if title:
        lines.append(indent + title)
    for key, value in data:
        lines.append(styled(line, key, value, w=width, lc=lcolor, rc=rcolor))
    return '\n'.join(lines)


class Contextual(
    argparse.RawDescriptionHelpFormatter,
    argparse.ArgumentDefaultsHelpFormatter
):

    def _format_action(self, action):
        help = super(Contextual, self)._format_action(action)
        sep = ' ' * self._indent_increment
        parts = help.split(sep)
        left = styled('{bright}{}{reset}', sep.join(parts[:-1]))
        right = parts[-1]
        return sep.join([left, right])

    def add_usage(self, usage, actions, groups, prefix=None):

        parent = getattr(self, 'parent', None)
        if parent:
            usage = parent.usage
            description = parent.description
        else:
            description = None

        prefix = 'Usage: '
        super(Contextual, self).add_usage(usage, actions, groups, prefix)
        if description:
            self.add_text('\n' + description)
        # self.add_text(format_context() + '\n')

    def add_section(self, header, lines):
        self.start_section(header)
        self.add_lines(lines)
        self.end_section()

    def add_lines(self, lines):
        def format_lines(*args):
            cind = self._current_indent * ' '
            text = cind + (('\n' + cind).join(args))
            return text
        self._add_item(format_lines, lines)


class Root(Contextual):

    def add_usage(self, usage, actions, groups, prefix=None):
        super(Root, self).add_usage(usage, actions, groups, prefix)
        self.add_text(format_context() + '\n')
        self.add_text(format_commands())
        # self.add_text(format_actions())
