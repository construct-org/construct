# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

__all__ = ['OptToken', 'opt_format', 'Template']


class OptToken(object):

    def __init__(self, value, default, parent, found):
        self.value = value
        self.default = default
        self.parent = parent
        self.found = found

    def __str__(self):
        return self.value if self.found else self.default

    def __getitem__(self, item):
        if item in self.parent:
            return OptToken(
                self.value + self.parent[item],
                self.default,
                self.parent,
                True
            )
        return OptToken(
            self.value + item,
            self.default,
            self.parent,
            self.found
        )


class Template(str):

    def format(self, *args, **kwargs):
        kwargs['opt'] = OptToken('', '', kwargs, False)
        return super(Template, self).format(*args, **kwargs)

    def fields(self):
        tokens = []
        for token in self._formatter_parser():
            if not token[1]:
                continue

            name = token[1]
            if name.startswith('opt'):
                insq = False
                chars = ''
                for char in name:
                    if insq and char not in '[]':
                        chars += char
                    if char == '[':
                        insq = True
                    if char == ']':
                        insq = False
                        if len(chars) > 1:
                            tokens.append(chars)
                        chars = ''
            else:
                tokens.append(name)
        return tokens


def opt_format(tmpl, *args, **kwargs):
    '''Format a string containing optional tokens.

    Examples:

        >>> tmpl = 'This is a {opt[adjective][ ]}string.'
        >>> opt_format(tmpl)
        'This is a string.'
        >>> opt_format(tmpl, adjective='super')
        'This is a super string.'
    '''
    kwargs['opt'] = OptToken('', '', kwargs, False)
    return tmpl.format(*args, **kwargs)
