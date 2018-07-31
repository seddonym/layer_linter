=======
History
=======

0.1.0 (2018-06-20)
------------------

* First release on PyPI.

0.2.0 (2018-06-23)
------------------

* Look for ``layers.yaml`` in current working directory.

0.3.0 (2018-06-24)
------------------

* Rename command to ``layer-lint``.
* Changed order of layers in ``layers.yaml`` to be listed high level to low level.

0.4.0 (2018-07-22)
------------------

* Made dependency analysis more efficient and robust.
* Improved report formatting.
* Removed illegal dependencies that were implied by other, more succinct illegal dependencies.
* Added ``--debug`` command line argument.

latest
------

* Added count of analysed files and dependencies to report.
* Fixed issues from running command in a different directory to the package.
* Increased speed of analysis. 
