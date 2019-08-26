# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import print_function
import sys

# Mock stuff
try:
    from unittest import mock
except:
    import mock
sys.modules['Qt'] = mock.MagicMock()
sys.modules['Qt.QtCore'] = mock.MagicMock()
sys.modules['Qt.QtGui'] = mock.MagicMock()
sys.modules['Qt.QtWidgets'] = mock.MagicMock()

# Local imports
from construct import resources
# Local imports
import construct
from . import setup_api, teardown_api, data_dir


def setup_module():
    setup_api(__name__)


def teardown_module():
    teardown_api(__name__)


def test_builtin_resources():
    '''Load and find builtin resources.'''

    r = resources.BuiltinResources()
    r.load()

    assert r._loaded
    assert r.find(':/styles/dark.css')
    assert r.find(':/styles/light.css')

    try:
        r.find(':/doesnot/exist.png')
        assert False, 'Expected ResourceNotFoundError.'
    except resources.ResourceNotFoundError:
        assert True

    # Only load once
    new_r = resources.BuiltinResources()
    assert new_r._loaded


def test_api_resources():
    '''Find API resources.'''

    api = construct.API(__name__)

    # Create fake resources to locate
    tmp_dir = data_dir(__name__, 'tmp')
    settings_dir = api.settings.folder
    files = [
        (tmp_dir / 'icons/unique01.png' ),
        (tmp_dir / 'icons/multiple.png' ),
        (tmp_dir / 'styles/dark.css' ),
        (tmp_dir / 'styles/unique01.css' ),
        (settings_dir / 'icons/unique02.png' ),
        (settings_dir / 'icons/multiple.png' ),
        (settings_dir / 'styles/dark.css' ),
        (settings_dir / 'styles/unique02.css' ),
    ]
    for file in files:
        file.parent.mkdir(parents=True, exist_ok=True)
        file.touch()

    api.path.insert(0, tmp_dir)

    # Expected resolution order
    # builtins -> tmp_dir -> settings
    resource_dir = resources.this_package
    tests = [
        ('icons/unique01.png', files[0]), # Unique to tmp_dir
        ('icons/multiple.png', files[1]), # First available
        ('styles/dark.css', files[2]), # Builtin overriden by api resource
        ('styles/unique01.css', files[3]), # Unique to tmp_dir
        ('icons/unique02.png', files[4]), # Unique to settings_dir
        ('styles/unique02.css', files[7]), # Unique to settings dir
        (':/styles/dark.css', resource_dir / 'styles/dark.css'), # : force b-in
        ('styles/light.css', resource_dir / 'styles/light.css'), # only in b-in
    ]
    for resource, expected_path in tests:
        resource_path = api.resources.find(resource)
        err = '%s: %s != %s' % (resource, resource_path, expected_path)
        assert resource_path.samefile(expected_path), err
