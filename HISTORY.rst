=======
History
=======

0.1.0 (2018-06-20)
------------------

* First release on PyPI.

0.2.0 (2018-06-23)
------------------

* Look for ``layers.yml`` in current working directory.

0.3.0 (2018-06-24)
------------------

* Rename command to ``layer-lint``.
* Changed order of layers in ``layers.yml`` to be listed high level to low level.

0.4.0 (2018-07-22)
------------------

* Made dependency analysis more efficient and robust.
* Improved report formatting.
* Removed illegal dependencies that were implied by other, more succinct illegal dependencies.
* Added ``--debug`` command line argument.

0.5.0 (2018-08-01)
------------------

* Added count of analysed files and dependencies to report.
* Fixed issues from running command in a different directory to the package.
* Increased speed of analysis.
* Changed ``--config_directory`` command line argument to ``--config-directory``.

0.6.0 (2018-08-07)
------------------

* Added ability to whitelist paths.

0.6.1 (2018-08-07)
------------------

* Add current working directory to path.

0.6.2 (2018-08-17)
------------------

* Don't analyse children of directories that aren't Python packages.
* Prevented installing incompatible version of Pydeps (1.6).

0.7.0 (2018-09-04)
------------------

* Complete rewrite of static analysis used to build dependency graph.
* Added quiet and verbose reporting.
* Added type annotation and mypy.
* Build earlier versions of Python using pybackwards.
* Corrected docs to refer to ``layers.yml`` instead of ``layers.yaml``.

0.7.1 (2018-09-04)
------------------

* Fix packaging bug with 0.7.0.

