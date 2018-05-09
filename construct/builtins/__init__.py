# -*- coding: utf-8 -*-
from __future__ import absolute_import
from construct.extension import Extension
from construct.utils import package_path
from construct.builtins import (
    projects,
    sequences,
    shots,
    assets,
    tasks,
    templates,
    workspaces,
    files,
)


class Builtins(Extension):
    '''Builtin Actions and Tasks'''

    name = 'Builtins'
    attr_name = 'builtins'

    def available(self, ctx):
        return True

    def load(self):

        self.add_template_path(package_path('builtins/templates'))

        self.add_action(projects.NewProject)
        self.add_task(projects.NewProject, projects.stage_project)
        self.add_task(projects.NewProject, projects.validate_project)
        self.add_task(projects.NewProject, projects.commit_project)

        self.add_action(sequences.NewSequence)
        self.add_task(sequences.NewSequence, sequences.stage_sequence)
        self.add_task(sequences.NewSequence, sequences.validate_sequence)
        self.add_task(sequences.NewSequence, sequences.commit_sequence)

        self.add_action(shots.NewShot)
        self.add_task(shots.NewShot, shots.stage_shot)
        self.add_task(shots.NewShot, shots.validate_shot)
        self.add_task(shots.NewShot, shots.commit_shot)

        self.add_action(assets.NewAsset)
        self.add_task(assets.NewAsset, assets.stage_asset)
        self.add_task(assets.NewAsset, assets.validate_asset)
        self.add_task(assets.NewAsset, assets.commit_asset)

        self.add_action(assets.NewAssetType)
        self.add_task(assets.NewAssetType, assets.stage_asset_type)
        self.add_task(assets.NewAssetType, assets.validate_asset_type)
        self.add_task(assets.NewAssetType, assets.commit_asset_type)

        self.add_action(tasks.NewTask)
        self.add_task(tasks.NewTask, tasks.stage_task)
        self.add_task(tasks.NewTask, tasks.validate_task)
        self.add_task(tasks.NewTask, tasks.commit_task)

        self.add_action(workspaces.NewWorkspace)
        self.add_task(workspaces.NewWorkspace, workspaces.stage_workspace)
        self.add_task(workspaces.NewWorkspace, workspaces.validate_workspace)
        self.add_task(workspaces.NewWorkspace, workspaces.commit_workspace)

        self.add_action(templates.NewTemplate)
        self.add_task(templates.NewTemplate, templates.stage_template)
        self.add_task(templates.NewTemplate, templates.validate_template)
        self.add_task(templates.NewTemplate, templates.commit_template)

        self.add_action(files.Publish)
        self.add_action(files.PublishFile)

        self.add_action(files.Open)
        self.add_task(files.Open, files.open_file)

        self.add_action(files.Save)
        self.add_task(files.Save, files.build_filename)
        self.add_task(files.Save, files.save_file)
