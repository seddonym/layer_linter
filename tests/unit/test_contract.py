from unittest import mock
import pytest
from layer_linter import contract
from layer_linter.dependencies import ImportPath
from layer_linter.contract import Contract, Layer
import logging
import sys

logger = logging.getLogger('layer_linter')
logging.getLogger('pydeps').setLevel(logging.ERROR)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class TestContractCheck:
    def test_kept_contract(self):
        contract = Contract(
            name='Foo contract',
            packages=(
                'foo',
            ),
            layers=(
                Layer('three'),
                Layer('two'),
                Layer('one'),
            ),
            whitelisted_paths=mock.sentinel.whitelisted_paths,
        )
        dep_graph = mock.Mock()
        dep_graph.find_path.return_value = None
        dep_graph.get_descendants.return_value = []

        contract.check_dependencies(dep_graph)

        assert contract.is_kept is True

        # Check that each of the possible disallowed imports were checked
        dep_graph.find_path.assert_has_calls((
            mock.call(downstream='foo.one', upstream='foo.two',
                      ignore_paths=mock.sentinel.whitelisted_paths),
            mock.call(downstream='foo.one', upstream='foo.three',
                      ignore_paths=mock.sentinel.whitelisted_paths),
            mock.call(downstream='foo.two', upstream='foo.three',
                      ignore_paths=mock.sentinel.whitelisted_paths),
        ))

    def test_broken_contract(self):
        contract = Contract(
            name='Foo contract',
            packages=(
                'foo',
            ),
            layers=(
                Layer('three'),
                Layer('two'),
                Layer('one'),
            ),
        )
        dep_graph = mock.Mock()
        dep_graph.get_descendants.return_value = []
        # Mock that one imports two and three, and two imports three
        dep_graph.find_path.side_effect = [
            None,
            ['foo.one', 'foo.two'],
            ['foo.one', 'foo.three'],
            ['foo.two', 'foo.three']
        ]

        contract.check_dependencies(dep_graph)

        assert contract.is_kept is False

        # Check that each of the possible disallowed imports are checked
        dep_graph.find_path.assert_has_calls((
            mock.call(downstream='foo.one', upstream='foo.two',
                      ignore_paths=[]),
            mock.call(downstream='foo.one', upstream='foo.three',
                      ignore_paths=[]),
            mock.call(downstream='foo.two', upstream='foo.three',
                      ignore_paths=[]),
        ))

    def test_unchecked_contract_raises_exception(self):
        contract = Contract(
            name='Foo contract',
            packages=(
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

    def test_broken_contract_children(self):
        contract = Contract(
            name='Foo contract',
            packages=(
                'foo',
            ),
            layers=(
                Layer('two'),
                Layer('one'),
            ),
        )
        dep_graph = mock.Mock()
        # Mock some deeper submodules
        dep_graph.get_descendants.side_effect = [
            # For foo.one
            ['foo.one.alpha', 'foo.one.alpha.red', 'foo.one.alpha.green', 'foo.one.beta'],
            # For foo.two
            [],
        ]

        # Mock that foo.one.alpha.red imports foo.two
        dep_graph.find_path.side_effect = [
            None, None,
            ['foo.one.alpha.red', 'foo.two'],
            None, None
        ]

        contract.check_dependencies(dep_graph)

        assert contract.is_kept is False

        # Check that each of the possible disallowed imports are checked
        dep_graph.find_path.assert_has_calls((
            mock.call(downstream='foo.one', upstream='foo.two',
                      ignore_paths=[]),
            mock.call(downstream='foo.one.alpha', upstream='foo.two',
                      ignore_paths=[]),
            mock.call(downstream='foo.one.alpha.red', upstream='foo.two',
                      ignore_paths=[]),
            mock.call(downstream='foo.one.alpha.green', upstream='foo.two',
                      ignore_paths=[]),
            mock.call(downstream='foo.one.beta', upstream='foo.two',
                      ignore_paths=[]),
        ))

    def test_broken_contract_via_other_layer(self):
        # If an illegal import happens via another layer, we don't want to report it
        # (as it will already be reported).

        contract = Contract(
            name='Foo contract',
            packages=(
                'foo',
            ),
            layers=(
                Layer('three'),
                Layer('two'),
                Layer('one'),
            ),
        )
        dep_graph = mock.Mock()
        dep_graph.get_descendants.return_value = []
        # Mock that one imports two, and two imports three
        dep_graph.find_path.side_effect = [
            ['foo.one', 'foo.two'],
            ['foo.one', 'foo.two', 'foo.three'],
            ['foo.two', 'foo.three'],
        ]

        contract.check_dependencies(dep_graph)

        assert contract.illegal_dependencies == [
            ['foo.one', 'foo.two'],
            ['foo.two', 'foo.three'],
        ]

    @pytest.mark.parametrize('longer_first', (True, False))
    def test_only_shortest_violation_is_reported(self, longer_first):
        contract = Contract(
            name='Foo contract',
            packages=(
                'foo',
            ),
            layers=(
                Layer('two'),
                Layer('one'),
            ),
        )
        dep_graph = mock.Mock()
        dep_graph.get_descendants.side_effect = [
            # For foo.one
            ['foo.one.alpha', 'foo.one.alpha.red', 'foo.one.alpha.green', 'foo.one.beta'],
            # For foo.two
            [],
        ]
        # These are both dependency violations, but it's more useful just to report
        # the more direct violation (the second one in this case).
        if longer_first:
            dep_graph.find_path.side_effect = [
                # foo.one <- foo.two
                None,
                # foo.one.alpha <- foo.two
                ['foo.one.alpha', 'foo.one.alpha.green', 'foo.x.alpha', 'foo.two'],
                # foo.one.alpha.red <- foo.two
                ['foo.one.alpha.red', 'foo.one.alpha.green', 'foo.x.alpha', 'foo.two'],
                # foo.one.alhpa.green <- foo.two
                ['foo.one.alpha.green', 'foo.x.alpha', 'foo.two'],
                # foo.one.beta <- foo.two
                None,
            ]
        else:
            dep_graph.find_path.side_effect = [
                None,
                ['foo.one.alpha', 'foo.x.alpha', 'foo.two'],
                None,
                ['foo.one.alpha.green', 'foo.one.alpha', 'foo.x.alpha', 'foo.two'],
                None,
            ]

        contract.check_dependencies(dep_graph)

        if longer_first:
            assert contract.illegal_dependencies == [
                ['foo.one.alpha.green', 'foo.x.alpha', 'foo.two'],
            ]
        else:
            assert contract.illegal_dependencies == [
                ['foo.one.alpha', 'foo.x.alpha', 'foo.two'],
            ]


class TestContractFromYAML:
    def test_incorrect_whitelisted_path_format(self):
        data = {
            'layers': ['one', 'two'],
            'whitelisted_paths': [
                'not the right format',
            ]
        }

        with pytest.raises(ValueError) as exception:
            contract.contract_from_yaml('Contract Foo', data)
        assert str(exception.value) == (
            'Whitelisted paths must be in the format '
            '"importer.module <- imported.module".'
        )
