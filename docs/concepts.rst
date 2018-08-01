=============
Core concepts
=============

Layer Linter has two key concepts, the *Layer* and the *Contract*.

Layers are a concept used in software architecture. They are used to describe
the organizing of an application into distinct sections, or 'layers'.
Each layer is concerned with a different level of detail. For example,
a three-tier architecture may involve a data layer, a domain layer and an
interface layer. The data layer is concerned with the lowest level (storage),
while the interface layer is concerned with the highest level (receiving/validating user input).
In the middle is the domain layer, which takes care of business logic.

Typically, the lower level layers will be ignorant of higher levels. This means
that something in the domain layer can use utilities provided by the data layer,
but not the other way around. In other words, there is a dependency flow from
low to high.

Layer Linter focuses on this dependency flow within a single Python codebase. It
sees layers as sets of Python modules or packages that exist at the same
level of the project hierarchy, and have a prescribed dependency flow.

Simple 3-tier architecture
--------------------------

The three-tier architecture described above might be organised in Python the following way:

.. code-block:: none

    myproject/
        interface.py
        domain.py
        data.py

However, in Python there is no built in way of enforcing the dependency flow of
``data`` to ``domain`` to ``interface``. This is where the concept of a *Contract* comes in.
You can use a contract to prescribe this dependency flow. This can be represented
in yaml format:

.. code-block:: none

    Three-tier contract:
        packages:
            myproject
        layers:
            - interface
            - domain
            - data

This has three components:

1. **Name**: in this case, 'Three-tier contract'. This can be anything you like,
   and is just used when reporting a broken contract.
2. **Packages**: This lists each package that contains the layers. In this case,
   our layers are at the top level, so we only specify the top-level package.
3. **Layers**: A list of the modules (or subpackages) to be treated as layers.
   The order runs from high level to low level.

N.B. Layers do not have to be standalone modules (i.e. single ``.py`` files). The
contract above could also apply to a codebase whose layers are subpackages like this:

.. code-block:: none

    myproject/
        interface/
            __init__.py
            urls.py
            views.py
            forms.py
        domain/
            __init__.py
            billing.py
            products.py
            users.py
        data/
            __init__.py
            billing.py
            products.py
            users.py

Modular layers
--------------

An alternative, more modular style is to implement layers as a repeated pattern
*within* subpackages, like so:

.. code-block:: none

    myproject/
        billing/
            interface.py
            domain.py
            data.py
        products/
            interface.py
            domain.py
            data.py
        users/
            interface.py
            domain.py
            data.py

This could be described in a contract as follows:

.. code-block:: none

    Modular Contract:
        packages:
            - myproject.billing
            - myproject.products
            - myproject.users
        layers:
            - interface
            - domain
            - data

Multiple contracts
------------------

You may also wish to have multiple contracts. Take the following example:

.. code-block:: none

    Top level:
        packages:
            myproject
        layers:
            - billing
            - products
            - users

    Modular three-tier:
        packages:
            - myproject.billing
            - myproject.products
            - myproject.users
        layers:
            - interface
            - domain
            - data

This would enforce dependency flow both *within your modules* (``data`` to ``domain`` to ``interface``)
and also *between them* (``users`` to ``products`` to ``billing``).

(For further reading on Layers, see
`the Wikipedia page on Multitier Architecture`_).

.. _`the Wikipedia page on Multitier Architecture`: https://en.wikipedia.org/wiki/Multitier_architecture

Whitelisting paths
------------------

Sometimes, you may wish to tolerate certain dependencies that do not adhere to your contract.
To do this, include them as *whitelisted paths* in your contract.

Let's say you have a project that follows a three tier architecture, but you
have a ``utils`` module that introduces a circular dependency between two of your layers. The report
might look something like this:

.. code-block:: none

    ----------------
    Broken contracts
    ----------------


    My layer contract
    -----------------

    1. myproject.packagetwo.lowlevelmodule imports myproject.packagetwo.highlevelmodule:

        myproject.packagetwo.lowlevelmodule <-
        myproject.utils <-
        myproject.packagetwo.highlevelmodule

If you want to suppress this error, you can add one component of the path to the contract like so:

.. code-block:: none

    My Layers Contract:
      packages:
        - myproject.packageone
        - myproject.packagetwo
        - myproject.packagethree
      layers:
        - highlevelmodule
        - mediumlevelmodule
        - lowlevelmodule
      whitelisted_paths:
        - myproject.packagetwo.lowlevelmodule <- myproject.utils

Running the linter again will show the contract passing.

There are a few use cases:

- Your project does not completely adhere to the contract, but you want to prevent it getting worse.
  You can whitelist any known issues, and gradually fix them.
- You have an exceptional circumstance in your project that you are comfortable with,
  and don't wish to fix.
- You want to understand how many dependencies you would need to fix before a project
  conforms to a particular architecture. Because Layer Linter only shows the most direct
  dependency violation, whitelisting paths can reveal less direct ones.
