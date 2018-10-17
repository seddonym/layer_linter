from unittest import mock
import importlib
import pytest
from layer_linter import contract
from layer_linter.module import Module
from layer_linter.contract import Contract, Layer
import logging
import sys

logger = logging.getLogger('layer_linter')
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class StubDependencyGraph:
    """
    Stub of the DependencyGraph for use in tests.

    Args:
        descendants: Dictionary keyed with Modules, whose values are the descendants of
                     those modules. This should not include the module itself.
        paths:       Nested dictionary, in the form:

                     {
                        upstream_module: {
                            downstream_module: [downstream_module, ..., upstream_module],
                            ...
                        }
                        ...
                     }
                    A call to .find_path(downstream=downstream_module, upstream=upstream_module)
                    will return the supplied path, if it is present in the dictionary. Otherwise,
                    the stub will return None.
        modules:    List of all modules in the graph.
    Usage:

        graph = StubDependencyGraph(
            descendants={
                Module('foo.one'): [
                    Module('foo.one.red'), Module('foo.one.green')
                ],
            },
            paths = {
                Module('foo.one.green'): {
                    Module('foo.three.blue.alpha'): [
                        Module('foo.one.green'), Module('baz'), Module('foo.three.blue.alpha')
                    ],
                },
                ...
            },
            modules [Module('foo.one'), Module('foo.one.red'), Module('foo.one.green')],
        )

    """
    def __init__(self, descendants=None, paths=None, modules=None):
        self.descendants = descendants if descendants else {}
        self.paths = paths if paths else {}
        self.modules = modules if modules else []

    def get_descendants(self, module):
        try:
            return self.descendants[module]
        except KeyError:
            return []

    def find_path(self, downstream, upstream, ignore_paths=None):
        try:
            return self.paths[upstream][downstream]
        except KeyError:
            return None

    def __contains__(self, item):
        return item in self.modules


class TestContractCheck:
    def test_kept_contract(self):
        contract = Contract(
            name='Foo contract',
            containers=(
                Module('foo.blue'),
                Module('foo.green'),
            ),
            layers=(
                Layer('three'),
                Layer('two'),
                Layer('one'),
            ),
            whitelisted_paths=mock.sentinel.whitelisted_paths,
        )
        graph = StubDependencyGraph(
            descendants={
                Module('foo.green.one'): [
                    Module('foo.green.one.alpha'),
                    Module('foo.green.one.beta'),
                ],
                Module('foo.green.three'): [
                    Module('foo.green.three.alpha'),
                    Module('foo.green.three.beta'),
                ],
            },
            paths={
                # Include some allowed paths.
                Module('foo.blue.two'): {
                    # Layer directly importing a layer below it.
                    Module('foo.blue.three'): [Module('foo.blue.three'), Module('foo.blue.two')],
                },
                Module('foo.blue.one'): {
                    # Layer directly importing two layers below.
                    Module('foo.blue.three'): [Module('foo.blue.three'), Module('foo.blue.one')],
                },
                Module('foo.green.three'): {
                    # Layer importing higher up layer, but from another container.
                    Module('foo.blue.one'): [Module('foo.blue.one'), Module('foo.green.three')],
                },
                Module('foo.green.three.beta'): {
                    # Module inside layer importing another module in same layer.
                    Module('foo.green.three.alpha'): [Module('foo.green.three.alpha'),
                                                      Module('foo.green.three.beta')],
                },
                Module('foo.green.one.alpha'): {
                    # Module inside layer importing a module inside a lower layer.
                    Module('foo.green.three.alpha'): [Module('foo.green.three.alpha'),
                                                      Module('foo.green.one.alpha')]
                },
            },
            modules=[
                Module('foo.green'),
                Module('foo.green.one'),
                Module('foo.green.one.alpha'),
                Module('foo.green.one.beta'),
                Module('foo.green.two'),
                Module('foo.green.three'),
                Module('foo.blue'),
                Module('foo.blue.one'),
                Module('foo.blue.two'),
                Module('foo.blue.three'),
            ]
        )

        contract.check_dependencies(graph)

        assert contract.is_kept is True

    def test_broken_contract(self):
        contract = Contract(
            name='Foo contract',
            containers=(
                Module('foo.blue'),
                Module('foo.green'),
            ),
            layers=(
                Layer('three'),
                Layer('two'),
                Layer('one'),
            ),
        )
        graph = StubDependencyGraph(
            descendants={
                Module('foo.green.one'): [
                    Module('foo.green.one.alpha'),
                    Module('foo.green.one.beta'),
                ],
                Module('foo.green.three'): [
                    Module('foo.green.three.alpha'),
                    Module('foo.green.three.beta'),
                ],
            },
            paths={
                Module('foo.blue.two'): {
                    # An allowed path: layer directly importing a layer below it.
                    Module('foo.blue.three'): [Module('foo.blue.three'), Module('foo.blue.two')],
                    # Disallowed path: layer directly importing a layer above it.
                    Module('foo.blue.one'): [Module('foo.blue.one'), Module('foo.blue.two')],
                },
                Module('foo.green.three.alpha'): {
                    # Module inside layer importing a module inside a higher layer.
                    Module('foo.green.one.alpha'): [Module('foo.green.one.alpha'),
                                                    Module('foo.green.three.alpha')],
                },
            },
            modules=[
                Module('foo.green'),
                Module('foo.green.one'),
                Module('foo.green.one.alpha'),
                Module('foo.green.one.beta'),
                Module('foo.green.two'),
                Module('foo.green.three'),
                Module('foo.blue'),
                Module('foo.blue.one'),
                Module('foo.blue.two'),
                Module('foo.blue.three'),
            ]
        )

        contract.check_dependencies(graph)

        assert contract.is_kept is False
        assert contract.illegal_dependencies == [
            [Module('foo.blue.one'), Module('foo.blue.two')],
            [Module('foo.green.one.alpha'), Module('foo.green.three.alpha')]
        ]

    def test_unchecked_contract_raises_exception(self):
        contract = Contract(
            name='Foo contract',
            containers=(
                'foo',
            ),
            layers=(
                Layer('three'),
                Layer('two'),
                Layer('one'),
            ),
        )

        with pytest.raises(RuntimeError) as excinfo:
            contract.is_kept
        assert 'Cannot check whether contract is ' \
            'kept until check_dependencies is called.' in str(excinfo.value)

    def test_broken_contract_via_other_layer(self):
        # If an illegal import happens via another layer, we don't want to report it
        # (as it will already be reported).

        contract = Contract(
            name='Foo contract',
            containers=(
                'foo',
            ),
            layers=(
                Layer('three'),
                Layer('two'),
                Layer('one'),
            ),
        )
        graph = StubDependencyGraph(
            descendants={},
            paths={
                Module('foo.three'): {
                    Module('foo.two'): [Module('foo.two'), Module('foo.three')],
                    Module('foo.one'): [Module('foo.one'), Module('foo.two'), Module('foo.three')],
                },
                Module('foo.two'): {
                    Module('foo.one'): [Module('foo.one'), Module('foo.two')],
                },
            },
            modules=[
                Module('foo.one'),
                Module('foo.two'),
                Module('foo.three'),
            ]
        )

        contract.check_dependencies(graph)

        assert contract.illegal_dependencies == [
            [Module('foo.one'), Module('foo.two')],
            [Module('foo.two'), Module('foo.three')],
        ]

    

    @pytest.mark.parametrize('longer_first', (True, False))
    def test_only_shortest_violation_is_reported(self, longer_first):
        contract = Contract(
            name='Foo contract',
            containers=(
                'foo',
            ),
            layers=(
                Layer('two'),
                Layer('one'),
            ),
        )

        # These are both dependency violations, but it's more useful just to report
        # the more direct violation.
        if longer_first:
            paths = {
                Module('foo.two'): {
                    Module('foo.one.alpha'): [
                        Module('foo.one.alpha'), Module('foo.one.alpha.green'),
                        Module('foo.another'), Module('foo.two'),
                    ],
                    Module('foo.one.alpha.green'): [
                        Module('foo.one.alpha.green'), Module('foo.another'), Module('foo.two'),
                    ],

                },
            }
        else:
            paths = {
                Module('foo.two'): {
                    Module('foo.one.alpha'): [
                        Module('foo.one.alpha'), Module('foo.another'), Module('foo.two'),
                    ],
                    Module('foo.one.alpha.green'): [
                        Module('foo.one.alpha.green'), Module('foo.one.alpha'),
                        Module('foo.another'), Module('foo.two'),
                    ],

                },
            }
        graph = StubDependencyGraph(
            descendants={
                Module('foo.one'): [Module('foo.one.alpha'), Module('foo.one.beta'),
                                    Module('foo.one.alpha.blue'), Module('foo.one.alpha.green')],
            },
            paths=paths,
            modules=[Module('foo.one'), Module('foo.two')]
        )

        contract.check_dependencies(graph)

        if longer_first:
            assert contract.illegal_dependencies == [
                [Module('foo.one.alpha.green'), Module('foo.another'), Module('foo.two')],
            ]
        else:
            assert contract.illegal_dependencies == [
                [Module('foo.one.alpha'), Module('foo.another'), Module('foo.two')],
            ]

    def test_missing_contract_raises_exception(self):
        contract = Contract(
            name='Foo contract',
            containers=(
                'foo.one',
                'foo.two',
            ),
            layers=(
                Layer('blue'),
                Layer('yellow'),  # Missing from foo.two.
                Layer('green'),
            ),
        )
        graph = StubDependencyGraph(
            modules=[
                Module('foo.one'),
                Module('foo.one.blue'),
                Module('foo.one.blue.alpha'),
                Module('foo.one.yellow'),
                Module('foo.one.green'),
                Module('foo.two'),
                Module('foo.two.blue'),
                Module('foo.two.blue.alpha'),
                Module('foo.two.green'),
            ]
        )

        with pytest.raises(ValueError) as e:
            contract.check_dependencies(graph)

        assert str(e.value) == (
            "Missing layer in container 'foo.two': module foo.two.yellow does not exist."
        )


@mock.patch.object(importlib.util, 'find_spec')
class TestContractFromYAML:

    def test_incorrect_whitelisted_path_format(self, mock_find_spec):
        data = {
            'containers': ['mypackage.foo', 'mypackage.bar'],
            'layers': ['one', 'two'],
            'whitelisted_paths': [
                'not the right format',
            ]
        }

        with pytest.raises(ValueError) as exception:
            contract.contract_from_yaml('Contract Foo', data, 'mypackage')
        assert str(exception.value) == (
            'Whitelisted paths must be in the format '
            '"importer.module <- imported.module".'
        )

    def test_container_not_in_package(self, mock_find_spec):
        data = {
            'containers': ['mypackage.foo', 'anotherpackage.foo'],
            'layers': ['one', 'two'],
        }

        with pytest.raises(ValueError) as exception:
            contract.contract_from_yaml('Contract Foo', data, 'mypackage')
        assert str(exception.value) == (
            "Invalid container 'anotherpackage.foo': containers must be either a subpackage of "
            "'mypackage', or 'mypackage' itself."
        )
