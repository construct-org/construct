# -*- coding: utf-8 -*-

from __future__ import absolute_import

# Local imports
from .cache import Cache, UserCache
from .software import Software


extensions = [
    Software,
    Cache,
    UserCache,
]
