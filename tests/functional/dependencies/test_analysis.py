import os
import sys

from layer_linter.dependencies.analysis import DependencyAnalyzer
from layer_linter.dependencies.path import ImportPath


class TestDependencyAnalyzer:
    def test_success(self):
        modules = [
            'analyzerpackage',
            'analyzerpackage.utils',
            'analyzerpackage.one',
            'analyzerpackage.one.alpha',
            'analyzerpackage.one.beta',
            'analyzerpackage.one.gamma',
            'analyzerpackage.two',
            'analyzerpackage.two.alpha',
            'analyzerpackage.two.beta',
            'analyzerpackage.two.gamma',
        ]
        assets_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',
                                                   'assets'))
        path = os.path.join(assets_path, 'analyzerpackage')
        os.chdir(path)
        sys.path.append(path)
        package = __import__('analyzerpackage')

        analyzer = DependencyAnalyzer(modules, package)
        import_paths = analyzer.determine_import_paths()

        # N.B. We expect only the leaf imports, it's just noise to have parent packages
        # in the graph too.
        expected_import_path_tuples = (
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
