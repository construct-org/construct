# -*- coding: utf-8 -*-
import six

try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path

try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping

if six.PY2:
    import functools
    _assignments = functools.WRAPPER_ASSIGNMENTS
    _updates = functools.WRAPPER_UPDATES
    def wraps(wrapped, assigned=_assignments, updated=_updates):
        members = dir(wrapped)
        assigned = set(members) & set(assigned)
        updated = set(members) & set(updated)
        return functools.wraps(wrapped, assigned, updated)
else:
    from functools import wraps
