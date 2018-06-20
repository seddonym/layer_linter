============
Layer Linter
============


.. image:: https://img.shields.io/pypi/v/layer_linter.svg
        :target: https://pypi.python.org/pypi/layer_linter

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
are following a self-imposed layered architecture within your Python project.

You create a `layers.yaml` file which defines the order in which different modules
within your project may import from each other. Layer Linter will parse the file,
analyse the internal dependencies within your project, and error if you are violating
your prescribed layers architecture.

For more information, see the documentation_.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _documentation: https://layer-linter.readthedocs.io
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
