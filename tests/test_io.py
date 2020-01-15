# -*- coding: utf-8 -*-

from __future__ import absolute_import

# Local imports
import construct

# Local imports
from . import setup_api, teardown_api


def setup_module():
    setup_api(__name__)


def teardown_module():
    teardown_api(__name__)


# TODO: Improve io testing by using fixtures
#       Currently inadequate but do provide a slim layer of validation


def test_new_projects():
    '''Create two new projects'''

    api = construct.API(__name__)

    project = api.io.new_project(
        name='project',
        location='local',
        mount='projects',
        data={'is_project': True, 'is_library': False}
    )
    project_path = api.io.get_path_to(project)
    assert (project_path / '.data').exists()
    assert project_path.exists()
    assert project['is_project']
    assert not project['is_library']

    library = api.io.new_project(
        name='library',
        location='local',
        mount='lib',
        data={'is_project': False, 'is_library': True}
    )
    library_path = api.io.get_path_to(library)
    assert (library_path / '.data').exists()
    assert library_path.exists()
    assert library['is_library']
    assert not library['is_project']


def test_new_asset():
    '''Create a new asset'''

    api = construct.API(__name__)
    project = api.io.new_project(
        name='project_w_asset',
        location='local',
        mount='projects',
    )

    asset = api.io.new_asset(
        project,
        name='Asset_A',
        bin='assets',
        asset_type='asset',
    )

    # New asset should create data on disk
    asset_path = api.io.get_path_to(asset)
    assert (asset_path / '.data').exists()

    # As well as store a small subset of data in a project's assets dict
    project_assets = api.io.get_project_by_id(project['_id'])['assets']
    project_asset = project_assets[asset['name']]

    project_asset_keys = set(['_id', 'name', 'bin', 'asset_type', 'group'])
    assert project_asset_keys == set(project_asset.keys())

    # The data stored in the project should match the data stored at the
    # asset level.
    for key in project_asset_keys:
        assert asset['_id'] == project_asset['_id']


def test_bins():
    '''Test bins io methods'''

    api = construct.API(__name__)

    # New project has default bins
    project = api.io.new_project(
        name='bin_project',
        location='local',
        mount='projects',
    )
    assert 'bins' in project
    assert 'assets' in project['bins']
    assert 'shots' in project['bins']

    # get_bins returns bins from project
    bins = api.io.get_bins(project)
    assert bins == project['bins']

    # passing just project_id still returns bins
    bins = api.io.get_bins({'_id': project['_id']})
    assert bins == project['bins']

    # create a new bin
    new_bin = api.io.new_bin(project, name='new_bin')
    assert new_bin['name'] == 'new_bin'
    assert new_bin['order'] == 2
    assert new_bin['icon'] == ''

    # ensure exists in project data
    project = api.io.get_project(name='bin_project')
    assert new_bin['name'] in project['bins']

    # update bin
    upd_bin = api.io.update_bin(
        project=project,
        name='new_bin',
        data={'icon': 'upd_icon', 'name': 'upd_bin'}
    )
    assert upd_bin['name'] == 'upd_bin'
    assert upd_bin['icon'] == 'upd_icon'

    project = api.io.get_project(name='bin_project')
    assert upd_bin['name'] in project['bins']
    assert new_bin['name'] not in project['bins']

    # delete bin
    api.io.delete_bin(project, name='new_bin')
    project = api.io.get_project(name='project')
    assert upd_bin['name'] not in project['bins']


def test_asset_types():
    '''Test asset_types io methods'''

    api = construct.API(__name__)

    # New project has default asset_types
    project = api.io.new_project(
        name='asset_type_project',
        location='local',
        mount='projects',
    )
    assert 'asset_types' in project
    assert 'asset' in project['asset_types']
    assert 'shot' in project['asset_types']

    # get_asset_types returns asset_types from project
    asset_types = api.io.get_asset_types(project)
    assert asset_types == project['asset_types']

    # passing just project_id still returns asset_types
    asset_types = api.io.get_asset_types({'_id': project['_id']})
    assert asset_types == project['asset_types']

    # create a new asset_type
    new_asset_type = api.io.new_asset_type(project, name='new_asset_type')
    assert new_asset_type['name'] == 'new_asset_type'
    assert new_asset_type['order'] == 2
    assert new_asset_type['icon'] == ''

    # ensure exists in project data
    project = api.io.get_project(name='asset_type_project')
    assert new_asset_type['name'] in project['asset_types']

    # update asset_type
    upd_asset_type = api.io.update_asset_type(
        project=project,
        name='new_asset_type',
        data={'icon': 'upd_icon', 'name': 'upd_asset_type'}
    )
    assert upd_asset_type['name'] == 'upd_asset_type'
    assert upd_asset_type['icon'] == 'upd_icon'

    project = api.io.get_project(name='asset_type_project')
    assert upd_asset_type['name'] in project['asset_types']
    assert new_asset_type['name'] not in project['asset_types']

    # delete asset_type
    api.io.delete_asset_type(project, name='new_asset_type')
    project = api.io.get_project(name='project')
    assert upd_asset_type['name'] not in project['asset_types']


def test_task_types():
    '''Test task_types io methods'''

    api = construct.API(__name__)

    # New project has default task_types
    project = api.io.new_project(
        name='task_type_project',
        location='local',
        mount='projects',
    )
    assert 'task_types' in project
    assert 'model' in project['task_types']
    assert 'animate' in project['task_types']

    # get_task_types returns task_types from project
    task_types = api.io.get_task_types(project)
    assert task_types == project['task_types']

    # passing just project_id still returns task_types
    task_types = api.io.get_task_types({'_id': project['_id']})
    assert task_types == project['task_types']

    # create a new task_type
    new_task_type = api.io.new_task_type(
        project,
        name='new_task_type',
        short='ntt',
    )
    assert new_task_type['name'] == 'new_task_type'
    assert new_task_type['short'] == 'ntt'
    assert new_task_type['icon'] == ''

    # ensure exists in project data
    project = api.io.get_project(name='task_type_project')
    assert new_task_type['name'] in project['task_types']

    # update task_type
    upd_task_type = api.io.update_task_type(
        project=project,
        name='new_task_type',
        data={'icon': 'upd_icon', 'name': 'upd_task_type'}
    )
    assert upd_task_type['name'] == 'upd_task_type'
    assert upd_task_type['icon'] == 'upd_icon'

    project = api.io.get_project(name='task_type_project')
    assert upd_task_type['name'] in project['task_types']
    assert new_task_type['name'] not in project['task_types']

    # delete task_type
    api.io.delete_task_type(project, name='new_task_type')
    project = api.io.get_project(name='project')
    assert upd_task_type['name'] not in project['task_types']
