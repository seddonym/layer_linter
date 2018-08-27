import os
import sys

import pytest

from layer_linter.dependencies.analysis import DependencyAnalyzer
from layer_linter.dependencies.path import ImportPath
from layer_linter.module import Module


class TestDependencyAnalyzer:
    def test_success(self):
        modules = [
            Module('analyzerpackage'),
            Module('analyzerpackage.utils'),
            Module('analyzerpackage.one'),
            Module('analyzerpackage.one.alpha'),
            Module('analyzerpackage.one.beta'),
            Module('analyzerpackage.one.gamma'),
            Module('analyzerpackage.two'),
            Module('analyzerpackage.two.alpha'),
            Module('analyzerpackage.two.beta'),
            Module('analyzerpackage.two.gamma'),
        ]
        assets_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',
                                                   'assets'))
        path = os.path.join(assets_path, 'analyzerpackage')
        os.chdir(path)
        sys.path.append(path)
        package = Module('analyzerpackage')

        analyzer = DependencyAnalyzer(modules, package)
        import_paths = analyzer.determine_import_paths()

        # N.B. We expect only the leaf imports, it's just noise to have parent packages
        # in the graph too. However, if there is a separate parent import, that should be included.
        expected_import_path_tuples = (
            ('analyzerpackage.utils', 'analyzerpackage.one'),
            ('analyzerpackage.utils', 'analyzerpackage.two.alpha'),
            ('analyzerpackage.one.beta', 'analyzerpackage.one.alpha'),
            ('analyzerpackage.one.gamma', 'analyzerpackage.one.beta'),
            ('analyzerpackage.two.alpha', 'analyzerpackage.one.alpha'),
            ('analyzerpackage.two.beta', 'analyzerpackage.one.alpha'),
            ('analyzerpackage.two.gamma', 'analyzerpackage.two.beta'),
            ('analyzerpackage.two.gamma', 'analyzerpackage.utils'),
        )
        expected_import_paths = []
        for importer, imported in expected_import_path_tuples:
            expected_import_paths.append(
                ImportPath(importer=importer, imported=imported)
            )
        assert set(import_paths) == set(expected_import_paths)

    def test_all_different_import_types(self):
        """
        Test a single file with lots of different import types. Note that all of the other
        modules are empty files.
        """
        assets_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',
                                                   'assets'))
        path = os.path.join(assets_path, 'differentimporttypes')
        os.chdir(path)
        sys.path.append(path)
        package = Module('differentimporttypes')

        importer = Module('differentimporttypes.one.different_import_types')
        modules = [
            importer,
            Module('differentimporttypes'),
            Module('differentimporttypes.one'),
            Module('differentimporttypes.one.alpha'),
            Module('differentimporttypes.one.beta'),
            Module('differentimporttypes.one.gamma'),
            Module('differentimporttypes.one.gamma.foo'),
            Module('differentimporttypes.one.delta'),
            Module('differentimporttypes.one.epsilon'),
            Module('differentimporttypes.two'),
            Module('differentimporttypes.two.alpha'),
            Module('differentimporttypes.three'),
            Module('differentimporttypes.four'),
            Module('differentimporttypes.four.alpha'),
            # Some other modules, not imported.
            Module('differentimporttypes.five'),
            Module('differentimporttypes.five.alpha'),
        ]

        analyzer = DependencyAnalyzer(modules, package)
        import_paths = analyzer.determine_import_paths()

        expected_imported_modules = (
            Module('differentimporttypes.one'),
            Module('differentimporttypes.one.alpha'),
            Module('differentimporttypes.one.beta'),
            Module('differentimporttypes.one.gamma'),
            Module('differentimporttypes.one.gamma.foo'),
            Module('differentimporttypes.two.alpha'),
            Module('differentimporttypes.one.delta'),
            Module('differentimporttypes.one.epsilon'),
            Module('differentimporttypes.three'),
            Module('differentimporttypes.four.alpha'),
        )
        expected_import_paths = []
        for imported in expected_imported_modules:
            expected_import_paths.append(
                ImportPath(importer=importer, imported=imported)
            )
        assert set(import_paths) == set(expected_import_paths)
