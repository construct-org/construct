# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import shutil

import construct
from construct.utils import unipath
from construct.settings import restore_default_settings


this_dir = os.path.abspath(os.path.dirname(__file__))


def test_dir(*paths):
    return unipath(this_dir, *paths)


def data_dir(*paths):
    return test_dir('data', *paths)


def setup_api(name, **settings):
    settings_path = data_dir(name, 'settings')
    restore_default_settings(settings_path)
    api = construct.API(
        name,
        path=[settings_path],
        logging=dict(version=1)
    )
    settings.setdefault(
        "locations",
        {'local': {
            'projects': data_dir(name, 'projects').as_posix(),
            'lib': data_dir(name, 'lib').as_posix()
        }}
    )
    api.settings.update(**settings)
    api.settings.save()


def teardown_api(name):
    api = construct.API(name)
    api.uninit()
    app_dir = data_dir(name)
    shutil.rmtree(str(app_dir))
