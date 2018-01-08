# -*- coding: utf-8 -*-

try:
    basestring = basestring
except NameError:
    basestring = (str, bytes)
