# -*- coding: utf-8 -*-
from __future__ import absolute_import
from . import setup_api, teardown_api
from datetime import datetime
import construct


def setup_module():
    setup_api(__name__)


def teardown_module():
    teardown_api(__name__)


def test_user_caches():
    '''Test builtin cache types'''

    api = construct.API(__name__)

    cache_types = [api.cache, api.user_cache]

    for cache in cache_types:
        # Set a simple key
        value = 10
        cache.set('int', value)
        assert cache.get('int') == value

        # Set a list
        value = [0, 'X', 1, 'Z']
        cache.set('list', value)
        assert cache.get('list') == value

        # Set a dict - also roundtrip a datetime object
        value = {'str': 'string', 'date': datetime.utcnow(), 'list': [0]}
        cache.set('dict', value)
        assert cache.get('dict') == value

        # Delete a key
        key = 'int'
        cache.delete(key)
        assert key not in cache

        # Get a key with a default
        assert cache.get(key, 100) == 100

        # Clear the rest of the cache
        cache.clear()
        assert all([key not in cache for key in ['int', 'list', 'dict']])
