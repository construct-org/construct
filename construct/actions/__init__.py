# -*- coding: utf-8 -*-
from __future__ import absolute_import
from construct.actions.project import *
from construct.actions.sequences import *
from construct.actions.shots import *
from construct.actions.assets import *
from construct.actions.tasks import *
from construct.actions.templates import *
from construct.actions.workspaces import *
from construct.actions.save import *


def available(ctx):
    return True


def register(cons):
    '''Register all default actions'''

    # Project actions
    cons.action_hub.register(NewProject)
    cons.action_hub.connect(NewProject.identifier, make_new_project)

    # Sequence actions
    cons.action_hub.register(NewSequence)
    cons.action_hub.connect(NewSequence.identifier, make_new_sequence)

    # Shot actions
    cons.action_hub.register(NewShot)
    cons.action_hub.connect(NewShot.identifier, make_new_shot)

    # Asset actions
    cons.action_hub.register(NewAsset)
    cons.action_hub.connect(NewAsset.identifier, make_new_asset)

    # Task actions
    cons.action_hub.register(NewTask)
    cons.action_hub.connect(NewTask.identifier, stage_task)
    cons.action_hub.connect(NewTask.identifier, validate_task)
    cons.action_hub.connect(NewTask.identifier, commit_task)

    # Workspace actions
    cons.action_hub.register(NewWorkspace)
    cons.action_hub.connect(NewWorkspace.identifier, stage_workspace)
    cons.action_hub.connect(NewWorkspace.identifier, validate_workspace)
    cons.action_hub.connect(NewWorkspace.identifier, commit_workspace)

    # Template actions
    cons.action_hub.register(NewTemplate)
    cons.action_hub.connect(NewTemplate.identifier, stage_template_data)
    cons.action_hub.connect(NewTemplate.identifier, validate_template)
    cons.action_hub.connect(NewTemplate.identifier, commit_template)

    # Save actions
    cons.action_hub.register(Save)

    #Publish actions
    cons.action_hub.register(Publish)
    cons.action_hub.register(PublishFile)


def unregister(cons):
    '''Unregister all default actions'''

    # Project actions
    cons.action_hub.disconnect(NewProject.identifier, make_new_project)
    cons.action_hub.unregister(NewProject)

    # Sequence actions
    cons.action_hub.disconnect(NewSequence.identifier, make_new_sequence)
    cons.action_hub.unregister(NewSequence)

    # Shot actions
    cons.action_hub.disconnect(NewShot.identifier, make_new_shot)
    cons.action_hub.unregister(NewShot)

    # Asset actions
    cons.action_hub.disconnect(NewAsset.identifier, make_new_asset)
    cons.action_hub.unregister(NewAsset)

    # Task actions
    cons.action_hub.disconnect(NewTask.identifier, stage_task)
    cons.action_hub.disconnect(NewTask.identifier, validate_task)
    cons.action_hub.disconnect(NewTask.identifier, commit_task)
    cons.action_hub.unregister(NewTask)

    # Workspace actions
    cons.action_hub.disconnect(NewWorkspace.identifier, stage_workspace)
    cons.action_hub.disconnect(NewWorkspace.identifier, validate_workspace)
    cons.action_hub.disconnect(NewWorkspace.identifier, commit_workspace)
    cons.action_hub.unregister(NewWorkspace)

    # Template actions
    cons.action_hub.disconnect(NewTemplate.identifier, stage_template_data)
    cons.action_hub.disconnect(NewTemplate.identifier, validate_template)
    cons.action_hub.disconnect(NewTemplate.identifier, commit_template)
    cons.action_hub.unregister(NewTemplate)


    # Save actions
    cons.action_hub.unregister(Save)

    #Publish actions
    cons.action_hub.unregister(Publish)
    cons.action_hub.unregister(PublishFile)
