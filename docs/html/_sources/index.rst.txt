.. image:: https://img.shields.io/github/license/construct-org/construct.svg?style=flat-square
    :target: https://github.com/danbradham/construct/blob/master/LICENSE
    :alt: License

.. image:: https://img.shields.io/travis/construct-org/construct.svg?style=flat-square
    :target: https://travis-ci.org/danbradham/construct
    :alt: Travis

=========
construct
=========
An extensible API for creative project and asset management.


Features
========

 - Manage Projects on your file system
 - Integrate with your Creative Software
 - Manage Workspaces and Publishes
 - Folder and Path Templating (fsfs_ and Lucidity_)
 - Contextual API
 - Extensions, Actions, and Tasks


Core Packages
=============

+----------------------+------------------------------------------------+
| package              | description                                    |
+======================+================================================+
| construct_cpenv_     | Cpenv Integration for env management           |
+----------------------+------------------------------------------------+
| construct_launcher_  | Application launcher                           |
+----------------------+------------------------------------------------+
| construct_maya_      | Autodesk Maya integration                      |
+----------------------+------------------------------------------------+
| construct_nuke_      | The Foundry Nuke integration                   |
+----------------------+------------------------------------------------+
| construct_ui_        | Graphical user interface                       |
+----------------------+------------------------------------------------+


Installation
============

.. code-block:: console

    $ pip install git+ssh://git@github.com/construct-org/construct.git


.. toctree::
   :maxdepth: 2

   self
   concepts
   configuration
   environment
   cli
   guide
   api

.. _construct_cli: https://github.com/construct-org/construct_cli
.. _construct_cpenv: https://github.com/construct-org/construct_cpenv
.. _construct_templates: https://github.com/construct-org/construct_templates
.. _construct_launcher: https://github.com/construct-org/construct_launcher
.. _construct_maya: https://github.com/construct-org/construct_maya
.. _construct_nuke: https://github.com/construct-org/construct_nuke
.. _construct_ui: https://github.com/construct-org/construct_ui
.. _fsfs: https://github.com/danbradham/fsfs
.. _Lucidity: https://gitlab.com/4degrees/lucidity


* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
