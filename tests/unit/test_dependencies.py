from unittest.mock import patch, Mock

from layer_linter.dependencies import DependencyGraph


class TestDependencyGraph:
    SOURCES = {
        '__main__': {
            'foo': '-',
            'foo.one': '-',
            'foo.two': '-',
            'foo.three': '-',
            'foo.four': '-',
        },
        'foo.__main': {},
        'foo.one': {},
        'foo.two': {'foo.one': '-'},
        'foo.three': {'foo.two': '-'},
        'foo.four': {'foo.three': '-'},
    }
    PACKAGE = Mock(__name__='foo')

    def test_find_path_direct(self):
        with patch.object(DependencyGraph, '_generate_pydep_sources',
                          return_value=self.SOURCES):
            graph = DependencyGraph(self.PACKAGE)

        path = graph.find_path(upstream='foo.one', downstream='foo.two')

        assert path == ('foo.two', 'foo.one')

    def test_find_path_indirect(self):
        with patch.object(DependencyGraph, '_generate_pydep_sources',
                          return_value=self.SOURCES):
            graph = DependencyGraph(self.PACKAGE)

        path = graph.find_path(upstream='foo.one', downstream='foo.four')

        assert path == ('foo.four', 'foo.three', 'foo.two', 'foo.one',)

    def test_find_path_nonexistent(self):
        with patch.object(DependencyGraph, '_generate_pydep_sources',
                          return_value=self.SOURCES):
            graph = DependencyGraph(self.PACKAGE)

        path = graph.find_path(upstream='foo.four', downstream='foo.one')

        assert path is None

    def test_get_descendants_nested(self):
        sources = {
            'foo.one': [],
            'foo.one.alpha': [],
            'foo.one.beta': [],
            'foo.one.beta.green': [],
            'foo.two': ['foo.one'],
        }
        with patch.object(DependencyGraph, '_generate_pydep_sources'):
            graph = DependencyGraph(self.PACKAGE)
            graph._sources = sources

        assert set(graph.get_descendants('foo.one')) == {
            'foo.one.alpha',
            'foo.one.beta',
            'foo.one.beta.green',
        }

    def test_get_descendants_none(self):
        sources = {
            'foo.one': [],
            'foo.one.alpha': [],
            'foo.one.beta': [],
            'foo.one.beta.green': [],
            'foo.two': ['foo.one'],
        }
        with patch.object(DependencyGraph, '_generate_pydep_sources'):
            graph = DependencyGraph(self.PACKAGE)
            graph._sources = sources

        assert graph.get_descendants('foo.two') == []

    def test_module_count(self):
        with patch.object(DependencyGraph, '_generate_pydep_sources',
                          return_value=self.SOURCES):
            graph = DependencyGraph(self.PACKAGE)

        # Assert the module count is the number of sources.
        assert graph.module_count == 5

    def test_dependency_count(self):
        with patch.object(DependencyGraph, '_generate_pydep_sources',
                          return_value=self.SOURCES):
            graph = DependencyGraph(self.PACKAGE)

        assert graph.dependency_count == 3

