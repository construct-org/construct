=========
construct
=========

Creative project and asset management written in pure python. Highly customizable through the use of plugins, actions and templates.


Core Packages
=============

+----------------------+---------------------------------------------------+
| package              | description                                       |
+======================+===================================================+
| construct_cli_       | command line interface                            |
+----------------------+---------------------------------------------------+
| construct_ui_        | graphical user interface                          |
+----------------------+---------------------------------------------------+
| construct_launcher_  | application launcher                              |
+----------------------+---------------------------------------------------+
| construct_maya_      | Autodesk Maya integration                         |
+----------------------+---------------------------------------------------+
| construct_nuke_      | The Foundry Nuke integration                      |
+----------------------+---------------------------------------------------+
| construct_templates_ | default templates for projects, shots, and assets |
+----------------------+---------------------------------------------------+


Environment Variables
=====================

+-----------------------+------+----------------------+---------------------------------+
| variable              | type | default              | description                     |
+=======================+======+======================+=================================+
| CONSTRUCT_ROOT        | str  | cwd                  | Root directory of projects      |
+-----------------------+------+----------------------+---------------------------------+
| CONSTRUCT_PLUGIN_PATH | str  | ~/.construct/plugins | List of paths for plugin lookup |
+-----------------------+------+----------------------+---------------------------------+
| CONSTRUCT_USER        | str  | current user name    | Name of user                    |
+-----------------------+------+----------------------+---------------------------------+
| CONSTRUCT_DEBUG       | int  | 0                    | Disable/Enable debugging        |
+-----------------------+------+----------------------+---------------------------------+
| CONSTRUCT_HOST        | str  |                      | Name of current host            |
|                       |      |                      | (cli, maya, nuke, etc.)         |
+-----------------------+------+----------------------+---------------------------------+


Installation
============

.. code-block:: console

    $ pip install git+ssh://git@github.com/construct-org/construct.git


.. _construct_cli: https://github.com/construct-org/construct_cli
.. _construct_templates: https://github.com/construct-org/construct_cli
.. _construct_launcher: https://github.com/construct-org/construct_launcher
.. _construct_maya: https://github.com/construct-org/construct_maya
.. _construct_nuke: https://github.com/construct-org/construct_nuke
.. _construct_ui: https://github.com/construct-org/construct_ui
