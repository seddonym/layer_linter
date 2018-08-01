=====
Usage
=====

Before use, you will probably want to read :doc:`concepts`.

Defining your contracts
-----------------------

Your layers contracts are defined in a yaml file named ``layers.yaml``. This
may exist anywhere, but a good place is in your project root.

The file contains one or more contracts, in the following format:

.. code-block:: none

    [Contract name]
        packages:
            - [package]
            [...]
        layers:
            - [layer]
            - [layer]
            [...]
        whitelisted_paths:
            - [importing.module] <- [imported.module]
            - [importing.module] <- [imported.module]
            [...]

1. **Contract name**: A string to describe your contract.
2. **Package**: Absolute name of any Python package that contains the layers as
   immediate children. One or more packages are allowed in this list.
3. **Layer**: Name of the Python module relative to the each package listed in
   ``packages``. Modules lower down the list must not import modules higher up.
   (Remember, a Python module can either be a ``.py`` file or a directory with
   an ``__init__.py`` file inside.)
4. **Whitelisted paths** (optional): If you wish certain import paths not to
   break in the contract, you can optionally whitelist them.

For some examples, see :doc:`concepts`.

Running the linter
------------------

Layer Linter provides a single command: ``layer-lint``.

Running this will check that your project adheres to the contracts in your ``layers.yaml``.

- Positional arguments:

    - ``package_name``: The name of the Python package to validate (required).

- Optional arguments:

    - ``--config-directory``: The directory containing your ``layers.yaml``. If not
      supplied, Layer Linter will look in the current directory.
    - ``--debug``: Output debug messages when running the linter. No parameters required.

Default usage:

.. code-block:: none

    layer-lint myproject

Custom ``layers.yaml`` location:

.. code-block:: none

    layer-lint myproject --config-directory /path/to/directory
