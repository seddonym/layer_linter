from typing import Tuple, List
import os
import sys

import pytest

from layer_linter.dependencies.analysis import DependencyAnalyzer
from layer_linter.dependencies.path import ImportPath
from layer_linter.module import Module, SafeFilenameModule


class TestDependencyAnalyzer:
    def test_success(self):
        package = Module('analyzerpackage')
        modules = self._build_modules(
            package_name=package.name,
            tuples=(
                ('analyzerpackage', '__init__.py'),
                ('analyzerpackage.utils', 'utils.py'),
                ('analyzerpackage.one', 'one/__init__.py'),
                ('analyzerpackage.one.alpha', 'one/alpha.py'),
                ('analyzerpackage.one.beta', 'one/beta.py'),
                ('analyzerpackage.one.gamma', 'one/gamma.py'),
                ('analyzerpackage.two', 'two/__init__.py'),
                ('analyzerpackage.two.alpha', 'two/alpha.py'),
                ('analyzerpackage.two.beta', 'two/beta.py'),
                ('analyzerpackage.two.gamma', 'two/gamma.py'),
            ),
        )

        analyzer = DependencyAnalyzer(modules, package)
        import_paths = analyzer.determine_import_paths()

        # N.B. We expect only the leaf imports, it's just noise to have parent packages
        # in the graph too. However, if there is a separate parent import, that should be included.
        expected_import_paths = self._build_import_paths(
            tuples=(
                ('analyzerpackage.utils', 'analyzerpackage.one'),
                ('analyzerpackage.utils', 'analyzerpackage.two.alpha'),
                ('analyzerpackage.one.beta', 'analyzerpackage.one.alpha'),
                ('analyzerpackage.one.gamma', 'analyzerpackage.one.beta'),
                ('analyzerpackage.two.alpha', 'analyzerpackage.one.alpha'),
                ('analyzerpackage.two.beta', 'analyzerpackage.one.alpha'),
                ('analyzerpackage.two.gamma', 'analyzerpackage.two.beta'),
                ('analyzerpackage.two.gamma', 'analyzerpackage.utils'),
            )
        )

        assert set(import_paths) == set(expected_import_paths)

    def test_all_different_import_types(self):
        """
        Test a single file with lots of different import types. Note that all of the other
        modules are empty files.
        """
        package = Module('differentimporttypes')
        modules = self._build_modules(
            package_name=package.name,
            tuples=(
                # The first module is the one with the code we'll analyze.
                ('differentimporttypes.one.importer', 'one/importer.py'),
                ('differentimporttypes', '__init__.py'),
                ('differentimporttypes.one', 'one/__init__.py'),
                ('differentimporttypes.one.alpha', 'one/alpha.py'),
                ('differentimporttypes.one.beta', 'one/beta.py'),
                ('differentimporttypes.one.gamma', 'one/gamma/__init__.py'),
                ('differentimporttypes.one.gamma.foo', 'one/gamma/foo.py'),
                ('differentimporttypes.one.delta', 'one/delta.py'),
                ('differentimporttypes.one.epsilon', 'one/epsilon.py'),

                ('differentimporttypes.two', 'two/__init__.py'),
                ('differentimporttypes.two.alpha', 'two/alpha.py'),
                ('differentimporttypes.three', 'three.py'),
                ('differentimporttypes.four', 'four/__init__.py'),
                ('differentimporttypes.four.alpha', 'four/alpha.py'),
                # Some other modules, not imported.
                ('differentimporttypes.five', 'five/__init__.py'),
                ('differentimporttypes.five.alpha', 'five/alpha.py'),
            ),
        )

        analyzer = DependencyAnalyzer(modules, package)
        import_paths = analyzer.determine_import_paths()

        expected_import_paths = self._build_import_paths(
            tuples=(
                ('differentimporttypes.one.importer', 'differentimporttypes.one'),
                ('differentimporttypes.one.importer', 'differentimporttypes.one.alpha'),
                ('differentimporttypes.one.importer', 'differentimporttypes.one.beta'),
                ('differentimporttypes.one.importer', 'differentimporttypes.one.gamma'),
                ('differentimporttypes.one.importer', 'differentimporttypes.one.gamma.foo'),
                ('differentimporttypes.one.importer', 'differentimporttypes.two.alpha'),
                ('differentimporttypes.one.importer', 'differentimporttypes.one.delta'),
                ('differentimporttypes.one.importer', 'differentimporttypes.one.epsilon'),
                ('differentimporttypes.one.importer', 'differentimporttypes.three'),
                ('differentimporttypes.one.importer', 'differentimporttypes.four.alpha'),
            )
        )

        assert set(import_paths) == set(expected_import_paths)

    def test_import_from_within_init_file(self):
        # Relative imports from within __init__.py files should be interpreted as at the level
        # of the sibling modules, not the containing package.
        package = Module('initfileimports')
        modules = self._build_modules(
            package_name=package.name,
            tuples=(
                ('initfileimports', '__init__.py'),
                # This init file has ``from . import alpha``.
                ('initfileimports.one', 'one/__init__.py'),
                ('initfileimports.one.alpha', 'one/alpha.py'),  # The correct imported module.
                ('initfileimports.two', 'two/__init__.py'),
                ('initfileimports.alpha', 'alpha.py'),  # It shouldn't import this one.
            ),
        )

        analyzer = DependencyAnalyzer(modules, package)
        import_paths = analyzer.determine_import_paths()

        expected_import_paths = self._build_import_paths(
            tuples=(
                ('initfileimports.one', 'initfileimports.one.alpha'),
            )
        )

        assert set(import_paths) == set(expected_import_paths)

    def _build_modules(self,
                       package_name: str,
                       tuples: Tuple[Tuple[str, str]]) -> List[SafeFilenameModule]:
        package_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                '..', '..', 'assets', package_name, package_name,
            )
        )
        modules = []
        for module_name, module_filename in tuples:
            modules.append(
                SafeFilenameModule(
                    name=module_name,
                    filename=os.path.join(package_path, module_filename),
                )
            )
        return modules

    def _build_import_paths(self, tuples: Tuple[Tuple[str, str]]) -> List[ImportPath]:
        import_paths = []
        for importer, imported in tuples:
            import_paths.append(
                ImportPath(importer=Module(importer), imported=Module(imported))
            )
        return import_paths
