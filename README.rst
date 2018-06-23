============
Layer Linter
============


.. image:: https://img.shields.io/pypi/v/layer_linter.svg
        :target: https://pypi.python.org/pypi/layer_linter

.. image:: https://img.shields.io/pypi/pyversions/layer-linter.svg
    :alt: Python versions
    :target: http://pypi.python.org/pypi/layer-linter/

.. image:: https://img.shields.io/travis/seddonym/layer_linter.svg
        :target: https://travis-ci.org/seddonym/layer_linter

.. image:: https://codecov.io/gh/seddonym/layer_linter/branch/master/graph/badge.svg
        :target: https://codecov.io/gh/seddonym/layer_linter

.. image:: https://readthedocs.org/projects/layer-linter/badge/?version=latest
        :target: https://layer-linter.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/seddonym/layer_linter/shield.svg
     :target: https://pyup.io/repos/github/seddonym/layer_linter/
     :alt: Updates

Layer Linter checks that your project follows a custom-defined layered architecture.


* Free software: BSD license
* Documentation: https://layer-linter.readthedocs.io.


Overview
--------

Layer Linter can be used as part of an automated test suite to check that you
are following a self-imposed layered architecture within your Python project. This
is particularly useful if you are working on a complex codebase within a team,
when you want to enforce a particular architectural style.

To define how layers work within your project, you create a ``layers.yaml`` file.
This file prescribes the order in which different modules within your project may
import from each other.

Running the ``layer-linter`` command will parse the file, analyse your project's
internal dependencies within your project, and error if you are violating
your prescribed architecture.

Quick start
-----------

Install Layer Linter::

    pip install layer-linter

Create a ``layers.yaml`` in the root of your project, in this format:

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

From your project root, run::

    layer-linter myproject

If your code violates the contract, you will see an error message as follows:

.. code-block:: none

    Contracts: 0 kept, 1 broken.
    - Broken contract My Layers Contract:
      - myproject.packagetwo.mediumlevelmodule not allowed to import myproject.packagetwo.highlevelmodule.
