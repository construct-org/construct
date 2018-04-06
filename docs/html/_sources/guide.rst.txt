=========
API Guide
=========

Initialize Construct
====================
Before we can do anything useful with construct, we need to initialize it.

.. code-block:: python

    import construct
    construct.init()

The initialization process performs the following actions to configure
construct.

1. loads default config or config file set by CONSTRUCT_CONFIG env var
2. Configures logging for the "construct" namespace
3. Builds Context from your environment variables
4. Discovers Extensions in the following locations

    - construct.extensions entry_point
    - paths passed to construct.init
    - paths set in EXTENSION_PATHS config key
    - paths defined by CONSTRUCT_EXTENSION_PATHS env var

5. Loads Builtins Extension
6. Configures fsfs

Create a Project
==================

.. code-block:: python

    my_project = construct.new_project(
        root='~/projects/my_project',
        template='vfx_project'
    )


Create a Shot with an animation task
====================================

.. code-block:: python

    seq010 = construct.new_sequence(
        project=my_project,
        name='seq010',
        template='vfx_sequence'
    )
    sh010 = construct.new_shot(
        sequence=seq010,
        name='sh010',
        template='vfx_shot'
    )
    sh010_anim = construct.new_task(
        parent=sh010,
        type='animation'
    )


Create an Asset with a model task
=================================

.. code-block:: python

    coffee_cup = construct.new_asset(
        project=my_project,
        asset_type='prop',
        name='coffee_cup',
        template='vfx_asset'
    )
    coffee_cup_model = construct.new_task(
        parent=coffee_cup,
        type='model'
        template='vfx_task'
    )


Working with Context
====================
You can set the current context from a path...

.. code-block:: python

    construct.set_context_from_path('~/projects/my_project')

or from an Entry.

.. code-block:: python

    my_project = construct.search('my_project').one()
    construct.set_context_from_entry(my_project)

Get the Actions available in your current context...

.. code-block:: python

    available_actions = construct.actions.collect()

or in a specific context.

.. code-block:: python

    ctx = construct.Context.from_path('~/projects/other_project')
    other_actions = construct.actions.collect(ctx)


Searching
=========

Find all projects

.. code-block:: python

    all_projects = construct.search(tags=['project'])

Find one project

.. code-block:: python

    project = construct.search('my_project', tags=['project']).one()

Find all assets in a project

.. code-block:: python

    assets = project.assets


Find all model tasks in a project

.. code-block:: python

    model_tasks = project.children().tags('model', 'task')


Find all shots in a sequence

.. code-block:: python

    seq = project.sequences.name('seq010').one()
    shots = seq.shots


Find a nested Entry using a name selector

.. code-block:: python

    model_task = construct.search('my_project/coffee_cup/model')
