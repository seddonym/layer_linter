==========================
Migrating to Import Linter
==========================

If you would like to migrate from Layer Linter to `Import Linter`_, you can easily migrate your setup.

.. _Import Linter: https://github.com/seddonym/import-linter

Step One - Install
------------------

.. code-block:: text

    pip install import-linter

Step Two - Configure
--------------------

Import Linter uses INI instead of YAML to define its contracts. Create an ``.importlinter`` file in the same directory
as your ``layers.yml``. This is where your configuration will live.

Converting the format is simple.

Example ``layers.yml``:

.. code-block:: yaml

    Contract one:
        containers:
            - mypackage
        layers:
            - api
            - utils

    Contract two:
        # This is a comment.
        containers:
            - mypackage.foo
            - mypackage.bar
            - mypackage.baz
        layers:
            - top
            - middle
            - bottom
        whitelisted_paths:
            - mypackage.foo.bottom.alpha <- mypackage.foo.middle.beta


Equivalent ``.importlinter``:

.. code-block:: ini

    [importlinter]
    root_package = mypackage


    [importlinter:contract:1]
    name = Contract one
    type = layers
    containers=
        mypackage
    layers=
        api
        utils


    [importlinter:contract:2]
    # This is a comment.
    name = Contract two
    type = layers
    containers=
        mypackage.foo
        mypackage.bar
        mypackage.baz
    layers=
        top
        middle
        bottom
    ignore_imports=
        mypackage.foo.bottom.alpha -> mypackage.foo.middle.beta


Things to note:

- Import Linter requires the root package to be configured in the file, rather than passed to the command line.
- Each contract requires a ``type`` - this is because Import Linter supports other contract types.
- Each contract needs an arbitrary unique identifier in the INI section (in this case, ``1`` and ``2``).
- 'Whitelisted paths' has have been renamed to 'ignore imports'. The notation is similar except the arrow is reversed;
  the importing package is still listed first, the imported package second.

Step Three - Run
----------------

To lint your package, run:

.. code-block:: text

    lint-imports

Or, if your configuration file is in a different directory:

.. code-block:: text

    lint-imports --config=path/to/.importlinter


Key differences between the packages
------------------------------------

- You may notice slight differences in the imports Import Linter picks up on. The main example is that it does not
  ignore modules in ``migrations`` subpackages, while Layer Linter does.
- Import Linter allows you to use other contract types and even define your own.
- Import Linter allows you to analyse imports of external packages too (though these don't make sense in the context
  of a layers contract).

Further reading can be found in the `Import Linter documentation`_.

.. _Import Linter documentation: https://import-linter.readthedocs.io
