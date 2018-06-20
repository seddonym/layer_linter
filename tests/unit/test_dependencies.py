from unittest.mock import patch, Mock

from layer_linter.dependencies import DependencyGraph


class TestDependencyGraph:
    SOURCES = {
        'one': Mock(
            imports=[],
        ),
        'two': Mock(
            imports=['one'],
        ),
        'three': Mock(
            imports=['two'],
        ),
        'four': Mock(
            imports=['three'],
        ),
    }

    def test_find_path_direct(self):
        with patch.object(DependencyGraph, '_generate_pydep_sources',
                          return_value=self.SOURCES):
            graph = DependencyGraph('foo')

        path = graph.find_path(upstream='one', downstream='two')

        assert path == ('two', 'one')

    def test_find_path_indirect(self):
        with patch.object(DependencyGraph, '_generate_pydep_sources',
                          return_value=self.SOURCES):
            graph = DependencyGraph('foo')

        path = graph.find_path(upstream='one', downstream='four')

        assert path == ('four', 'three', 'two', 'one',)

    def test_find_path_nonexistent(self):
        with patch.object(DependencyGraph, '_generate_pydep_sources',
                          return_value=self.SOURCES):
            graph = DependencyGraph('foo')

        path = graph.find_path(upstream='four', downstream='one')

        assert path is None

    def test_get_descendants_nested(self):
        sources = {
            'foo.one': Mock(
                imports=[],
            ),
            'foo.one.alpha': Mock(
                imports=[],
            ),
            'foo.one.beta': Mock(
                imports=[],
            ),
            'foo.one.beta.green': Mock(
                imports=[],
            ),
            'foo.two': Mock(
                imports=['foo.one'],
            ),
        }
        with patch.object(DependencyGraph, '_generate_pydep_sources'):
            graph = DependencyGraph('foo')
            graph._pydep_graph = Mock(sources=sources)

        assert set(graph.get_descendants('foo.one')) == {
            'foo.one.alpha',
            'foo.one.beta',
            'foo.one.beta.green',
        }

    def test_get_descendants_none(self):
        sources = {
            'foo.one': Mock(
                imports=[],
            ),
            'foo.one.alpha': Mock(
                imports=[],
            ),
            'foo.one.beta': Mock(
                imports=[],
            ),
            'foo.one.beta.green': Mock(
                imports=[],
            ),
            'foo.two': Mock(
                imports=['foo.one'],
            ),
        }
        with patch.object(DependencyGraph, '_generate_pydep_sources'):
            graph = DependencyGraph('foo')
            graph._pydep_graph = Mock(sources=sources)

        assert graph.get_descendants('foo.two') == []
