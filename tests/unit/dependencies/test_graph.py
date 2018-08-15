from unittest.mock import patch, Mock

from layer_linter.dependencies import graph as graph_module
from layer_linter.dependencies.path import ImportPath


class DependencyAnalyzerStub:
    def __init__(self, modules, package):
        self.import_paths = [
            ImportPath(importer='foo.two', imported='foo.one'),
            ImportPath(importer='foo.three', imported='foo.two'),
            ImportPath(importer='foo.four', imported='foo.three'),
        ]

    def determine_import_paths(self):
        return self.import_paths


class PackageScannerStub:
    def __init__(self, package):
        self.modules = [
            'foo',
            'foo.one',
            'foo.one.alpha',
            'foo.one.beta',
            'foo.one.beta.green',
            'foo.two',
        ]

    def scan_for_modules(self):
        return self.modules


@patch.object(graph_module, 'DependencyAnalyzer', new=DependencyAnalyzerStub)
@patch.object(graph_module, 'PackageScanner', new=PackageScannerStub)
class TestDependencyGraph:
    PACKAGE = Mock(__name__='foo')

    def test_find_path_direct(self):
        graph = graph_module.DependencyGraph(self.PACKAGE)

        path = graph.find_path(upstream='foo.one', downstream='foo.two')

        assert path == ('foo.two', 'foo.one')

    def test_find_path_indirect(self):
        graph = graph_module.DependencyGraph(self.PACKAGE)

        path = graph.find_path(upstream='foo.one', downstream='foo.four')

        assert path == ('foo.four', 'foo.three', 'foo.two', 'foo.one',)

    def test_find_path_nonexistent(self):
        graph = graph_module.DependencyGraph(self.PACKAGE)

        path = graph.find_path(upstream='foo.four', downstream='foo.one')

        assert path is None

    def test_direct_ignore_path_is_ignored(self):
        ignore_paths = (
            ImportPath(
                importer='foo.two', imported='foo.one',
            ),
        )
        graph = graph_module.DependencyGraph(self.PACKAGE)

        path = graph.find_path(
            upstream='foo.one', downstream='foo.two',
            ignore_paths=ignore_paths)

        assert path is None

    def test_indirect_ignore_path_is_ignored(self):
        ignore_paths = (
            ImportPath(
                importer='foo.three', imported='foo.two',
            ),
        )
        graph = graph_module.DependencyGraph(self.PACKAGE)

        path = graph.find_path(
            upstream='foo.one', downstream='foo.four',
            ignore_paths=ignore_paths)

        assert path is None

    def test_get_descendants_nested(self):

        graph = graph_module.DependencyGraph(self.PACKAGE)

        assert set(graph.get_descendants('foo.one')) == {
            'foo.one.alpha',
            'foo.one.beta',
            'foo.one.beta.green',
        }

    def test_get_descendants_none(self):
        graph = graph_module.DependencyGraph(self.PACKAGE)

        assert graph.get_descendants('foo.two') == []

    def test_module_count(self):
        graph = graph_module.DependencyGraph(self.PACKAGE)

        # Assert the module count is the number of modules returned by
        # PackageScanner.scan_for_modules.
        assert graph.module_count == 6

    def test_dependency_count(self):
        graph = graph_module.DependencyGraph(self.PACKAGE)

        # Should be number of ImportPaths returned by DependencyAnalyzer.determine_import_paths.
        assert graph.dependency_count == 3
