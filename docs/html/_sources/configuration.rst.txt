=============
Configuration
=============

Construct uses yaml files for configuration. Here is the default configuration,
construct/defaults/construct.yaml. You can specify your own configuration by
creating your own yaml file, and pointing your CONSTRUCT_CONFIG environment
variable to it.


.. code-block::

    ROOT: '~/projects'
    EXTENSION_PATHS:
        - '~/.construct'
    EVENT_STREAM_DB: '~/.construct/eventstream.sqlite'
    DISABLE_EXTENSIONS: []

    LOGGING:
        version: 1
        formatters:
            simple:
                format: '%(levelname).1s:%(name)s> %(message)s'
        handlers:
            console:
                formatter: simple
                class: logging.StreamHandler
        loggers:
            construct:
                level: DEBUG
                handlers: [console]
                propagate: False


    STATUSES:
        - 'waiting'
        - 'in progress'
        - 'rendering'
        - 'pending'
        - 'rejected'
        - 'complete'


    TASK_TYPES:
        - model
        - rig
        - shade
        - texture
        - comp
        - light
        - layout


    PATH_TEMPLATES:
        asset_type: '{project}/assets/{asset_type}'
        asset: '{project}/assets/{asset_type}/{asset}'
        sequence: '{project}/sequences/{sequence}'
        shot: '{project}/sequences/{sequence}/{shot}'
        task: '{parent}/{task}'
        publish: '{task}/publish/{file_type}/{task}_{name}/v{:0>3d}'
        publish_file: '{task}_{name}_v{:0>3d}.{ext}'
        workspace: '{task}/work/{workspace}'
        workspace_file: '{task}_{name}_v{:0>3d}.{ext}'


    SOFTWARE:
        maya2017:
            host: 'maya'
            workspace: 'maya'
            identifier: 'launch.maya2017'
            description: 'Launch Autodesk Maya2017'
            default_workspace: 'maya'
            icon: './icons/maya.png'
            cmd:
                win:
                    path: C:/Program Files/Autodesk/Maya2017/bin/maya.exe
                    args: []
                linux:
                    path: /usr/autodesk/maya2017/bin/maya
                    args: []
                mac:
                    path: /Applications/Autodesk/maya2017/bin/maya
                    args: []
        maya2018:
            host: 'maya'
            identifier: 'launch.maya2018'
            description: 'Launch Autodesk Maya2018'
            default_workspace: 'maya'
            icon: './icons/maya.png'
            extensions: ['.ma', '.mb', '.fbx', '.obj', '.abc']
            cmd:
                win:
                    path: C:/Program Files/Autodesk/Maya2018/bin/maya.exe
                    args: []
                linux:
                    path: /usr/autodesk/maya2018/bin/maya
                    args: []
                mac:
                    path: /Applications/Autodesk/maya2018/bin/maya
                    args: []
        nuke11.1v2:
            host: 'nuke'
            identifier: 'launch.nuke11.1v2'
            description: 'Launch The Foundry Nuke11.1v2'
            default_workspace: 'nuke'
            icon: './icons/nuke.png'
            extensions: ['.nk']
            cmd:
                win:
                    path: C:/Program Files/Nuke11.1v2/Nuke11.1.exe
                    args: []
                linux:
                    path: /usr/local/Nuke11.1v2/Nuke11.1
                    args: []
                mac:
                    path: /Applications/Nuke11.1v2/Nuke11.1v2.app/Nuke11.1
                    args: []
        sublime:
            host: 'sublime'
            identifier: 'launch.sublimetext'
            description: 'Launch Sublimt Text 3'
            default_workspace: null
            icon: './icons/sublime.png'
            extensions: ['.txt', '.py', '.mel']
            cmd:
                win:
                    path: C:/Program Files/Sublime Text 3//subl.exe
                    args: []
                linux:
                    path: /usr/bin/subl
                    args: []
                mac:
                    path: /Applications/Sublime Text.app/Contents/SharedSupport/bin/subl
                    args: []


    FILE_TYPES:
        alembic:
            extensions: ['.abc']
        maya:
            extensions: ['.ma', '.mb']
        nuke:
            extensions: ['.nk']
        c4d:
            extensions: ['.c4d']
        photoshop:
            extensions: ['.psd', '.psb']
        illustrator:
            extensions: ['.ai']
