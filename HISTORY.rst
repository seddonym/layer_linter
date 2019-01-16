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

* Renamed command to ``layer-lint``.
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

* Added current working directory to path.

0.6.2 (2018-08-17)
------------------

* Don't analyse children of directories that aren't Python packages.
* Prevented installing incompatible version of Pydeps (1.6).

0.7.0 (2018-09-04)
------------------

* Completed rewrite of static analysis used to build dependency graph.
* Added quiet and verbose reporting.
* Added type annotation and mypy.
* Built earlier versions of Python using pybackwards.
* Corrected docs to refer to ``layers.yml`` instead of ``layers.yaml``.

0.7.1 (2018-09-04)
------------------

* Fixed packaging bug with 0.7.0.

0.7.2 (2018-09-05)
------------------

* Fixed bug with not checking all submodules of layer.

0.7.3 (2018-09-07)
------------------

* Dropped support for Python 3.4 and 3.5 and adjust packaging.

0.7.4 (2018-09-20)
------------------

* Tweaked command line error handling.
* Improved README and `Core Concepts` documentation.

0.8.0 (2018-09-29)
------------------

* Replace ``--config-directory`` parameter with ``--config`` parameter, which takes a file name instead.

0.9.0 (2018-10-13)
------------------

* Moved to beta version.
* Improved documentation.
* Better handling of invalid package names passed to command line.

0.10.0 (2018-10-14)
-------------------

* Renamed 'packages' to 'containers' in contracts.

0.10.1 (2018-10-14)
-------------------

* Improved handling of invalid containers.

0.10.2 (2018-10-17)
-------------------

* Error if a layer is missing.

0.10.3 (2018-11-2)
------------------

* Fixed RST rendering on PyPI.

0.11.0 (2018-11-5)
------------------

* Support defining optional layers.

0.11.1 (2019-1-16)
------------------

* Updated dependencies, especially switching to a version of PyYAML to
  address https://nvd.nist.gov/vuln/detail/CVE-2017-18342.

0.12.0 (2019-1-16)
------------------

* Fix parsing of relative imports within __init__.py files.
