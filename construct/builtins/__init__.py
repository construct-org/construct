# -*- coding: utf-8 -*-
from __future__ import absolute_import
from construct.extension import Extension
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
        self.add_action(projects.NewProject)
        self.add_task(projects.NewProject, projects.make_new_project)

        self.add_action(sequences.NewSequence)
        self.add_task(sequences.NewSequence, sequences.make_new_sequence)

        self.add_action(shots.NewShot)
        self.add_task(shots.NewShot, shots.make_new_shot)

        self.add_action(assets.NewAsset)
        self.add_task(assets.NewAsset, assets.make_new_asset)

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

        self.add_action(files.Save)
        self.add_action(files.Publish)
        self.add_action(files.PublishFile)
