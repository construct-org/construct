=================
API Documentation
=================

API Function
------------
.. autofunction:: construct.API

API Object
----------
.. autoclass:: construct.api.API
    :members:
    :show-inheritance:

Context
-------
.. autoclass:: construct.context.Context
    :members:
    :show-inheritance:

Builtin Events
--------------
The following events are builtin and may be useful in extending Construct.

+--------------+-----------+-----------------------------------+
|    event     | arguments |            description            |
+==============+===========+===================================+
| before_setup | api       | Sent before api initialization.   |
+--------------+-----------+-----------------------------------+
| after_setup  | api       | Sent after api initialization.    |
+--------------+-----------+-----------------------------------+
| before_close | api       | Sent before api uninitialization. |
+--------------+-----------+-----------------------------------+
| after_close  | api       | Sent after api uninitialization.  |
+--------------+-----------+-----------------------------------+

EventManager
------------
.. autoclass:: construct.events.EventManager
    :members:
    :show-inheritance:

Settings
--------
.. automodule:: construct.settings
    :members:
    :show-inheritance:

Path
----
.. autoclass:: construct.path.Path
    :members:
    :show-inheritance:

Utils
-----
.. automodule:: construct.utils
    :members:
    :show-inheritance:

Errors
------
.. automodule:: construct.errors
    :members:
    :show-inheritance:

Extension Types
---------------
.. autoclass:: construct.extensions.Extension
    :members:
    :show-inheritance:

.. autoclass:: construct.extensions.Host
    :members:
    :show-inheritance:

ExtensionManager
----------------
.. autoclass:: construct.extensions.ExtensionManager
    :members:
    :show-inheritance:

Builtin Extensions
------------------
.. autoclass:: construct.extensions.software.Software
    :members:
    :show-inheritance:
