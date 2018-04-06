======================
Command Line Interface
======================

.. code-block:: console

    $ construct
    Usage: construct <command|action> [options]

    Current Context
      host          cli
      root          ~/projects
      user          dbradham
      platform      win

    Commands
      version       Version information
      home          Go to root directory
      pop           Go back to last location
      push          Go to first search result
      search        Search for Entries
      read          Read metadata
      write         Write metadata
      tag           Tag a directory
      untag         Untag a directory

    Actions
      new.project   Create a new Project

    Options:
      -h, --help     show this help message and exit (default: False)
      -v, --verbose  verbose output (default: False)


Anatomy of the CLI
==================

Current Context
    Describes the context of your current working directory.

Commands
    These are universal commands that are always present. They provide core functionality like navigation, searching, reading and writing data, tagging and untagging directories, and version info about Construct.

Actions
    Actions are invoked the same way commands are, but, they differ in a few ways. Actions are contextual, so different Actions will be available depending on your current context. For example, the new.project Action is available when you are not in a project. When you are in a project, you'll have actions for creating assets, shots, tasks and launching application.

    Actions are also typically composed of several tasks that can have a complicated flow of execution. In turn, when called from the CLI detailed info on the execution of the Actions tasks is provided including any artifacts that were created. An artifact is something produced by an Action. For example, the new.project action creates a new folder on your file system containing some metadata.

Options
    Options are data you provide to a command or action. Actions frequently require options to produce the results you want. For example, the new.project Action requires a --root option that specifies the directory where the project should be created. The --help option is universal, you can provide it whenever you need help using the CLI.

Navigation Commands
===================
The construct cli has 4 main commands to help you navigate your projects.

home
    Navigates to your context's root directory. Usually where your projects
    are located.
push
    Navigates to the first result in a search by name or tag
pop
    Navigates
search
    Finds Entries by name or tag.


Create a new Project
====================
Construct has several builtin actions that can be used to create and manage your projects. Let's use the new.project, new.asset, and new.task Actions to build a new project. By the end of this section we will have created a new project named "my_project" with an asset named "coffee_cup" that contains a model task.

First we'll start by going to our construct root directory.

.. code-block:: console

    $ construct home
    ~/projects$

Now we can use new.project to create our project.

.. code-block:: console

    ~/projects$ construct new.project --root my_project
    ...
    Atrifacts
        project  ~/projects/my_project

You should see a nice and detailed report ending with an Artifacts section showing us the the new project that was created. Now let's dive into my_project and create our asset and tasks.

.. code-block:: console

    ~/projects$ construct search my_project
    ~/projects/my_project

    ~/projects$ construct push my_project
    ~/projects/my_project$ construct new.asset --name coffee_cup --asset_type prop
    ...
    Artifacts
        asset  ~/projects/my_project/assets/prop/coffee_cup

    ~/projects/my_project$ construct push cup
    ~/projects/my_project/assets/prop/coffee_cup$ construct new.task --type model
    ...
    Artifacts
        task  ~/projects/my_project/assets/prop/coffee_cup/model

    ~/projects/my_project/assets/prop/coffee_cup$ construct push model
    ~/projects/my_project/assets/prop/coffee_cup/model$
