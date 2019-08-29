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
import construct
from construct import resources
from . import setup_api, teardown_api, data_dir


def setup_module():
    setup_api(__name__)


def teardown_module():
    teardown_api(__name__)


def test_builtin_resources():
    '''Load and get builtin resources.'''

    r = resources.BuiltinResources()
    r._load()

    assert r._loaded
    assert r.get(':/styles/dark.css')
    assert r.get(':/styles/light.css')

    try:
        r.get(':/doesnot/exist.png')
        assert False, 'Expected ResourceNotFoundError.'
    except resources.ResourceNotFoundError:
        assert True

    # Only load once
    new_r = resources.BuiltinResources()
    assert new_r._loaded


def test_api_resources():
    '''Get API resources.'''

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
        ('styles/dark.css', files[2]), # Builtin overriden by tmp_dir resource
        ('styles/unique01.css', files[3]), # Unique to tmp_dir
        ('icons/unique02.png', files[4]), # Unique to settings_dir
        ('styles/unique02.css', files[7]), # Unique to settings dir
        (':/styles/dark.css', resource_dir / 'styles/dark.css'), # : builtin
        ('styles/light.css', resource_dir / 'styles/light.css'), # only builtin
    ]
    for resource, expected_path in tests:
        resource_path = api.resources.get(resource)
        err = '%s: %s != %s' % (resource, resource_path, expected_path)
        assert resource_path.samefile(expected_path), err
