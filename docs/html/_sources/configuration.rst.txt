=============
Configuration
=============
When starting up Construct will look for a construct.yaml file in the following locations:

1. Paths stored in the CONSTRUCT_PATH environment variable
2. Your USER_PATH ``~/.construct``

The first construct.yaml that is found becomes your settings folder. If no construct.yaml file is found a default settings structure is created in the last path checked (default: `~/.construct`). The settings folder contains user icons, extensions, templates and software configurations.

To share a configuration accross your stuiod set CONSTRUCT_PATH on your workstations to a network folder. You can also override the default lookup behavior by providing your own list of paths when initializing the Construct API.

::

    import construct
    api = construct.API(path=['~/.custom_path'])

.. note:: Settings files are validated prior to being loaded. This prevents Construct from running with faulty settings.

Settings folder structure
=========================

::

    extensions/
    icons/
    templates/
    software/
    construct.yaml

extensions folder
-----------------
Python modules and packages containing extensions folders. This is the location where Construct discovers and loads Extensions.

icons folder
------------
One of the locations where Construct will look for icons. When configuring software you can place custom
icons here and reference them using `icons/myicon.png`.

templates folder
----------------
Template files like a maya workspace.mel. These templates can be used in software configurations.

software folder
---------------
Individual software configuration files.

construct.yaml
--------------
The main settings file. By default it looks like this.
::

    locations:
        local:
            lib: ~/lib
            projects: ~/projects
    my_location: local
    my_mount: projects
    extensions: []
    logging:
        version: 1
        formatters:
            simple:
            format: '%(levelname).1s:%(name)s> %(message)s'
        handlers:
            console:
                class: logging.StreamHandler
                formatter: simple
        loggers:
            construct:
                handlers:
                    - console
                level: DEBUG


Builtin Settings
================
The builtin settings that must be included in your construct.yaml file.

locations
---------
A dictionary containing locations and file system mounts. These are used to lookup file system paths to projects, folders, assets, and files. The default locations value supports a simple local setup.

::

    locations:
        local:
            lib: ~/lib
            projects: ~/projects

For a multisite solution you can define multiple locations and OS specific mounts.

::

    locations:
        NY:
            lib:
                win: //ny-server/lib
                mac: /Volumes/ny-server/lib
                linux: /mnt/ny-server/lib
            projects:
                win: //ny-server/projects
                mac: /Volumes/ny-server/projects
                linux: /mnt/ny-server/projects
        LA:
            lib:
                win: //la-server/lib
                mac: /Volumes/la-server/lib
                linux: /mnt/la-server/lib
            projects:
                win: //la-server/projects
                mac: /Volumes/la-server/projects
                linux: /mnt/la-server/projects

my_location
-----------
The default location that Construct will use.

Default: ``local``

my_mount
--------
The default mount that Construct will use.

Default: ``projects``

extensions
----------
A list of extensions to import and load when Construct starts. This is where you would list extensions
installed using pip.

.. note:: Builtin Extensions and Extensions located in your settings `extensions` folder will be loaded automatically, they do not need to be included here.

default: ``[]``

logging
-------
A dictConfig used to configure logging.


Software Settings
=================
Software is configured in individual yaml files stored in the software settings folder. Let's take a look at how we would configure Autodesk Maya2019.

software/maya2019.yaml::

    label: Autodesk Maya 2019
    icon: icons/maya.png
    host: maya
    cmd:
        linux: /usr/Autodesk/Maya2019/bin/maya
        mac: /applications/Autodesk/Maya2019.app/bin/maya.exe
        win: C:/Program Files/Autodesk/Maya2019/bin/maya.exe
    args: []
    files:
        templates/workspace.mel: workspace.mel
    folders:
        - data
        - cache
    extensions: ['.ma', '.mb', '.fbx', '.abc', '.obj']
    env: {}

label
-----
The nice name for the software.

icon
----
The path to an icon relative to your settings folder.

host
----
The identifier of a ``Host`` extension that handles this software. Usually you will have to write your own ``Host`` extensions to support any meaningful integration with a piece of software.

cmd
---
OS specific paths to the software executables.

args
----
Args to pass to the software executable.

files
-----
Files to copy to the workspace root when created. Each key is the path to a template file and it's accompanying value is the path relative to the workspace root where it will be copied to.

folders
-------
A list of folders to create in the workspace root.

extensions
----------
A list of extensions that this software is able to open.

env
---
Environment variables to set when launching this software. When values are lists they will be prepended to your current Environment variables value. When values are strings they will override an existing Environment variable value.
