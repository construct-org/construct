========
Concepts
========

Context
=======
Construct has a strong sense of Context. The current Context is used to
determine which Extensions, Actions, Tasks and Templates are available.

:host: Host application cli, maya, nuke, etc...
:platform: win, linux, or mac
:root: Directory containing your projects
:user: Username
:project: Project Entry
:sequence: Sequence Entry - contains shots
:shot: Shot Entry - contains tasks
:asset_type: AssetType Entry - contains assets
:asset: Asset Entry - contains tasks
:task: Task Entry - where publishes and workspaces are stored
:workspace: Workspace Entry - where work files are stored
:file: Current workfile file


All Extensions, Actions, and Tasks implement an :meth:`available` method that
takes a Context object and returns True if available in that Context.


Extensions
==========
Extensions are the basic building blocks of Construct. They provide Actions,
Tasks, and Templates. All builtin actions and templates are provided by the
Builtins Extension. Extensions can provide Tasks to extend existing Actions or
provide their own Actions.


.. code-block:: python

    from construct import Extension

    class MyExtension(Extension):

        name = 'My Extension'
        attr_name = 'my_extension'

        def load(self):
            # setup extension
            # add Actions, Tasks, and template paths
            pass

        def available(self, ctx):
            # Return True if Extension is available in ctx
            return True


Actions
=======
Actions are interfaces to run a set of Tasks ordered by their respective
priorities and requirements. Let's take a look at the :class:`NewProject` Action provided by the Builtins Extension.


.. code-block:: python

    import construct
    from construct import Action

    class NewProject(Action):
        '''Create a new Project'''

        label = 'New Project'
        identifier = 'new.project'

        @staticmethod
        def parameters(ctx):
            params = dict(
                root={
                    'label': 'Project Root',
                    'required': True,
                    'type': types.String,
                    'help': 'project root directory',
                },
                template={
                    'label': 'Project Template',
                    'required': True,
                    'type': types.String,
                    'help': 'name of a project template',
                }
            )

            if not ctx:
                return params

            templates = list(construct.get_templates('project').keys())
            params['template']['options'] = templates
            if templates:
                params['template']['default'] = templates[0]

            return params

        @staticmethod
        def available(ctx):
            return not ctx.project


Tasks
=====
Tasks are decorated python functions that are added to an Action and ordered by
their respective priorities and requirements.

.. code-block:: python

    from construct.tasks import task, requires, success, returns, artifact

    @task
    @requires(success('other_task'))
    @returns(artifact('message'))
    def some_task():
        return 'other_task completed successfully'

This task is useless, but, it shows us a few neat things about Tasks. Our task
'some_task' requires the success of 'other_task' and returns an artifact named
'message'. Construct provides a rich set of decorators and functions to help
you setup the flow of your Actions. Tasks also remain callable after being
decorated, so you can run them on their own which is nice for testing.

.. code-block:: python

    assert some_task() == 'other_task completed successfully'
