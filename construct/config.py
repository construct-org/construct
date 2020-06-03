# -*- coding: utf-8 -*-
from __future__ import absolute_import
from construct.constants import DEFAULT_CONFIG
from construct.vendor import yaml
try:
    from collections import ChainMap
except ImportError:
    from chainmap import ChainMap


class Config(object):
    '''Config object that looks up values in the following order.

        1. context.project.data
        2. config.dict
        3. config.defaults
    '''

    defaults = {}

    with open(DEFAULT_CONFIG, 'r') as f:
        defaults.update(yaml.safe_load(f.read()))

    def __init__(self, *args, **kwargs):
        self.dict = dict(*args, **kwargs)

    def __str__(self):
        return str(self.flatten())

    def chain(self):
        '''Build chainmap for current context'''

        dicts = []

        from construct.api import get_context
        ctx = get_context()
        if ctx and ctx.project:
            data = dict(
                (k, v) for k, v in ctx.project.data.items()
                if k.isupper()
            )
            dicts.append(data)

        dicts.append(self.dict)
        dicts.append(self.defaults)
        return ChainMap(*dicts)

    def flatten(self):
        return dict(self.chain())

    def get(self, *args):
        return self.chain().get(*args)

    def __getitem__(self, item):
        return self.chain().__getitem__(item)

    def __setitem__(self, item, value):
        self.dict.__setitem__(item, value)

    def update(self, *args, **kwargs):
        self.dict.update(*args, **kwargs)
