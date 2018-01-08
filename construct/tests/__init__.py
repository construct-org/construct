# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
from functools import partial


# Convenient attributes and functions
root = os.path.dirname(__file__)
data = os.path.join(root, 'test_data')
test_path = partial(os.path.join, root)
data_path = partial(os.path.join, data)
