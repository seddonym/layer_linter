from unittest.mock import patch, call
import pytest

from layer_linter.contract import Contract
from layer_linter.report import Report


@pytest.fixture
def make_kept_contract():
    def _make_contract():
        contract = Contract('Foo contract', [], [])
        contract.check_dependencies(None)
        return contract
    return _make_contract


@pytest.fixture
def make_broken_contract():
    def _make_contract(name, illegal_dependencies=None):
        contract = Contract(name, [], [])
        if illegal_dependencies is None:
            illegal_dependencies = [
                ('foo.upstream', 'foo.downstream'),
            ]
        contract.illegal_dependencies = illegal_dependencies
        return contract
    return _make_contract


class TestReport:
    def assert_output(self, contracts, output_lines):
        self.report = Report()

        for contract in contracts:
            self.report.add_contract(contract)

        with patch('builtins.print') as mock_print:
            self.report.output()
            mock_print.assert_has_calls(
                [call(line) for line in output_lines]
            )

    def test_zero_contracts(self):
        self.assert_output(
            contracts=[],
            output_lines=(
                'No contracts found.',
            )
        )
        assert self.report.has_broken_contracts is False

    def test_single_kept_contract(self, make_kept_contract):
        self.assert_output(
            contracts=[make_kept_contract()],
            output_lines=(
                'Contracts: 1 kept, 0 broken.',
            )
        )
        assert self.report.has_broken_contracts is False

    def test_single_broken_contract_direct(self, make_broken_contract):
        contract = make_broken_contract(
            name='Foo',
            illegal_dependencies=[
                ('foo.two', 'foo.one'),
            ]
        )
        self.assert_output(
            contracts=[contract],
            output_lines=(
                'Contracts: 0 kept, 1 broken.',
                '- Broken contract Foo:',
                '  - foo.two not allowed to import foo.one.',
            )
        )
        assert self.report.has_broken_contracts is True

    def test_multiple_kept_and_broken_contracts(self, make_kept_contract, make_broken_contract):
        broken_contract_1 = make_broken_contract(
            name='Contract 1',
            illegal_dependencies=[
                ('foo.two', 'foo.one'),
            ]
        )
        broken_contract_2 = make_broken_contract(
            name='Contract 2',
            illegal_dependencies=[
                ('bar.two', 'bar.one'),
            ]
        )
        self.assert_output(
            contracts=[
                broken_contract_1,
                make_kept_contract(),
                broken_contract_2,
                make_kept_contract(),
                make_kept_contract()
            ],
            output_lines=(
                'Contracts: 3 kept, 2 broken.',
                '- Broken contract Contract 1:',
                '  - foo.two not allowed to import foo.one.',
                '- Broken contract Contract 2:',
                '  - bar.two not allowed to import bar.one.',
            )
        )
        assert self.report.has_broken_contracts is True

    def test_single_broken_contract_indirect(self, make_broken_contract):
        contract = make_broken_contract(
            name='Foo',
            illegal_dependencies=[
                ('foo.four', 'foo.three', 'foo.two', 'foo.one'),
            ]
        )
        self.assert_output(
            contracts=[contract],
            output_lines=(
                'Contracts: 0 kept, 1 broken.',
                '- Broken contract Foo:',
                '  - foo.four not allowed to import foo.one (via foo.three, foo.two).',
            )
        )
        assert self.report.has_broken_contracts is True

    def test_single_broken_contract_multiple_illegal_dependencies(self, make_broken_contract):
        contract = make_broken_contract(
            name='Foo',
            illegal_dependencies=[
                ('foo.four', 'foo.three', 'foo.two', 'foo.one'),
                ('bar.two', 'bar.one'),
            ]
        )
        self.assert_output(
            contracts=[contract],
            output_lines=(
                'Contracts: 0 kept, 1 broken.',
                '- Broken contract Foo:',
                '  - foo.four not allowed to import foo.one (via foo.three, foo.two).',
                '  - bar.two not allowed to import bar.one.',
            )
        )
        assert self.report.has_broken_contracts is True
