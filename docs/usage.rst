=====
Usage
=====

Before use, you will probably want to read :doc:`concepts`.

Defining your contracts
-----------------------

Your layers contracts are defined in a YAML file named ``layers.yml``. This
may exist anywhere, but a good place is in your project root.

The file contains one or more contracts, in the following format:

.. code-block:: none

    Contract name:
        containers:
            - mypackage.container
            ...
        layers:
            - layerone
            - layertwo
            ...
        whitelisted_paths:
            - mypackage.container.layertwo.module <- mypackage.container.layerone.module
            ...

1. **Contract name**: A string to describe your contract.
2. **Containers**: Absolute names of any Python package that contains the layers as
   immediate children. One or more containers are allowed in this list.
3. **Layers**: Names of the Python module *relative* to each container listed in
   ``containers``. Modules lower down the list must not import modules higher up.
   (Remember, a Python module can either be a ``.py`` file or a directory with
   an ``__init__.py`` file inside.)
4. **Whitelisted paths** (optional): If you wish certain import paths not to
   break in the contract, you can optionally whitelist them. The modules should be listed as
   absolute names, with the importing module first, and the imported module second.

For some examples, see :doc:`concepts`.

Additional syntax
-----------------

**Optional layers**

You may specify certain layers as optional, by enclosing the name in parentheses.

By default, Layer Linter will error if it cannot find the module for a particular layer.
Take the following contract:

.. code-block:: none

    My contract:
        containers:
            - mypackage.foo
            - mypackage.bar
        layers:
            - one
            - two

If the module ``mypackage.foo.two`` is missing, the contract will be broken. If you want
the contract to pass despite this, you can enclose the layer name in parentheses:

.. code-block:: none

    My contract:
        containers:
            - mypackage.foo
            - mypackage.bar
        layers:
            - one
            - (two)

Layer ``two`` is now optional, which means the contract will pass even though ``mypackage.bar.two``
is missing.

Running the linter
------------------

Layer Linter provides a single command: ``layer-lint``.

Running this will check that your project adheres to the contracts in your ``layers.yml``.

- Positional arguments:

    - ``package_name``: The name of the top-level Python package to validate (required).

- Optional arguments:

    - ``--config``: The YAML file describing your layer contract(s). If not
      supplied, Layer Linter will look for a file called ``layers.yml`` in the current directory.
    - ``--quiet``: Do not output anything if the contracts are all adhered to.
    - ``--verbose`` (or ``-v``): Output a more verbose report.
    - ``--debug``: Output debug messages when running the linter. No parameters required.

Default usage:;

.. code-block:: none

    layer-lint myproject

Using a different filename or location instead of ``layers.yml``:

.. code-block:: none

    layer-lint myproject --config path/to/alternative.yml
