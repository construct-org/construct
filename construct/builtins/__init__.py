# -*- coding: utf-8 -*-
from __future__ import absolute_import
from .software import Software
from .cache import Cache, UserCache

extensions = [
    Software,
    Cache,
    UserCache,
]
