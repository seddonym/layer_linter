from unittest import mock, skip
import pytest
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
                Layer('one'),
                Layer('two'),
                Layer('three'),
            ),
        )
        dep_graph = mock.Mock()
        dep_graph.find_path.return_value = None
        dep_graph.get_descendants.return_value = []

        contract.check_dependencies(dep_graph)

        assert contract.is_kept is True

        # Check that each of the possible disallowed imports were checked
        dep_graph.find_path.assert_has_calls((
            mock.call(downstream='foo.one', upstream='foo.two'),
            mock.call(downstream='foo.one', upstream='foo.three'),
            mock.call(downstream='foo.two', upstream='foo.three'),
        ))

    def test_broken_contract(self):
        contract = Contract(
            name='Foo contract',
            packages=(
                'foo',
            ),
            layers=(
                Layer('one'),
                Layer('two'),
                Layer('three'),
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
            mock.call(downstream='foo.one', upstream='foo.two'),
            mock.call(downstream='foo.one', upstream='foo.three'),
            mock.call(downstream='foo.two', upstream='foo.three'),
        ))

    def test_unchecked_contract_raises_exception(self):
        contract = Contract(
            name='Foo contract',
            packages=(
                'foo',
            ),
            layers=(
                Layer('one'),
                Layer('two'),
                Layer('three'),
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
                Layer('one'),
                Layer('two'),
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
            mock.call(downstream='foo.one', upstream='foo.two'),
            mock.call(downstream='foo.one.alpha', upstream='foo.two'),
            mock.call(downstream='foo.one.alpha.red', upstream='foo.two'),
            mock.call(downstream='foo.one.alpha.green', upstream='foo.two'),
            mock.call(downstream='foo.one.beta', upstream='foo.two'),
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
                Layer('one'),
                Layer('two'),
                Layer('three'),
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
