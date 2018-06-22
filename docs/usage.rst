=====
Usage
=====

Before use, it's important to understand Layer Linter's two key concepts,
the *Layer* and the *Contract*.

Layers
------

A 'layered architecture' is a pattern within software architecture that can mean
many different things, so let's define what it means for Layer Linter.

Layers are sets of Python modules or packages that exist at the same
level of the project hierarchy, and have a prescribed dependency flow.
Take, for example, the following project:

.. code-block:: none

    myproject/
        interface.py
        domain.py
        data.py

In this simple project, you might decide that you are breaking it into three layers.
At the lowest level is the data layer, concerned with storage. Next is the domain layer,
which takes care of business logic. Finally you have the interface layer, which receives
and validates user input before passing it to the domain layer. In this architecture,
*a layer must have no knowledge of any layers higher up*. So while the domain layer has knowledge
of the data layer, the data layer knows nothing of the domain or interface layers.

Practically speaking, in Python what this means is that higher level modules can import
lower level modules, but not the other way around.

Layers can be packages, too, such as in this example:

.. code-block:: none

    myproject/
        interface/
          urls.py
          views.py
          forms.py
        domain/
          billing.py
          users.py
          products.py
        data/
          billing.py
          users.py
          products.py

An alternative, more modular style is to implement layers as a repeated pattern *within* subpackages, like so:

.. code-block:: none

    myproject/
        billing/
            interface.py
            domain.py
            data.py
        users/
            interface.py
            domain.py
            data.py
        products/
            interface.py
            domain.py
            data.py

(For further reading on Layers, see
`the Wikipedia page on Multitier Architecture`_).

Contracts and the ``layers.yaml`` file
--------------------------------------

A *Contract* is an agreement to adhere to a particular layered architecture. For
example, you may wish to say that your layers are ``data``, ``domain`` and ``interface``,
in order from low to high level.

You define your Contracts in a ``layers.yaml`` file. Give your contract a name
(in this case 'My Layers Contract'), specify which packages this applies to,
and list your layers in order from low to high.

.. code-block:: none

    My Layers Contract:
      packages:
        - myproject
      layers:
        - lowlevelmodule
        - mediumlevelmodule
        - highlevelmodule

For the more modular style described above, you can specify multiple packages:

.. code-block:: none

    Modular Contract:
          packages:
            - myproject.billing
            - myproject.users
            - myproject.products
          layers:
            - lowlevelmodule
            - mediumlevelmodule
            - highlevelmodule

You may include multiple contracts in the same file.

Running the linter
------------------

Once your ``layers.yaml`` file is ready, run the following command to check. (Most likely
you will want to include this as part of your test run.)

.. code-block:: none

    layer-linter myproject

You may specify a custom location for ``layers.yaml`` with the ``--config-directory``
argument:

.. code-block:: none

    layer-linter myproject --config-directory path/to/layers.yaml

.. _`the Wikipedia page on Multitier Architecture`: https://en.wikipedia.org/wiki/Multitier_architecture
