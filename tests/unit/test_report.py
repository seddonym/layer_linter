from unittest.mock import MagicMock, patch, call, sentinel
import pytest

from layer_linter.contract import Contract
from layer_linter import report
from layer_linter.report import Report, ConsolePrinter


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


@patch.object(report, 'ConsolePrinter')
class TestReport:
    def _report_contracts(self, contracts):
        """
        Report on the supplied list of Contracts.
        """
        self.report = Report(dependencies=MagicMock())

        for contract in contracts:
            self.report.add_contract(contract)
        self.report.output()

    def test_zero_contracts(self, printer):
        self._report_contracts(contracts=[])

        printer.print_heading.assert_has_calls([
            call('Layer Linter', printer.HEADING_LEVEL_ONE),
            call('Contracts', printer.HEADING_LEVEL_TWO),
        ])
        printer.print_error.assert_called_once_with('No contracts found.')
        assert self.report.has_broken_contracts is False

    def test_single_kept_contract(self, printer, make_kept_contract):
        kept_contract = make_kept_contract()

        self._report_contracts([kept_contract])

        printer.print_heading.assert_has_calls([
            call('Layer Linter', printer.HEADING_LEVEL_ONE),
            call('Contracts', printer.HEADING_LEVEL_TWO),
        ])
        printer.print_contract_one_liner.assert_called_once_with(kept_contract, is_kept=True)
        printer.print_success.assert_called_once_with('Contracts: 1 kept, 0 broken.')
        assert self.report.has_broken_contracts is False

    def test_single_broken_contract_direct(self, printer, make_broken_contract):
        broken_contract = make_broken_contract(
            name='Foo',
            illegal_dependencies=[
                ('foo.two', 'foo.one'),
            ]
        )

        self._report_contracts([broken_contract])

        printer.print_heading.assert_has_calls([
            call('Layer Linter', printer.HEADING_LEVEL_ONE),
            call('Contracts', printer.HEADING_LEVEL_TWO),
        ])
        printer.print_contract_one_liner.assert_called_once_with(broken_contract, is_kept=False)
        printer.print_error.assert_has_calls([call('Contracts: 0 kept, 1 broken.')])
        printer.print_heading.assert_has_calls([
            call('Broken contracts', printer.HEADING_LEVEL_TWO,
                 style=printer.ERROR),
            call('Foo', printer.HEADING_LEVEL_THREE,
                 style=printer.ERROR),
        ])
        printer.print_error.assert_has_calls([
            call('1. foo.two imports foo.one:'),
            call('foo.two <-', bold=False),
            call('foo.one', bold=False),
        ])

        assert self.report.has_broken_contracts is True

    def test_multiple_kept_and_broken_contracts(self, printer, make_kept_contract,
                                                make_broken_contract):
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
        kept_contract_1 = make_kept_contract()
        kept_contract_2 = make_kept_contract()
        kept_contract_3 = make_kept_contract()
        self._report_contracts([
            broken_contract_1,
            kept_contract_1,
            broken_contract_2,
            kept_contract_2,
            kept_contract_3,
        ])

        printer.print_heading.assert_has_calls([
            call('Layer Linter', printer.HEADING_LEVEL_ONE),
            call('Contracts', printer.HEADING_LEVEL_TWO),
        ])
        printer.print_contract_one_liner.assert_has_calls([
            call(kept_contract_1, is_kept=True),
            call(kept_contract_2, is_kept=True),
            call(kept_contract_3, is_kept=True),
            call(broken_contract_1, is_kept=False),
            call(broken_contract_2, is_kept=False),
        ])
        printer.print_error.assert_has_calls([call('Contracts: 3 kept, 2 broken.')])
        printer.print_heading.assert_has_calls([
            call('Broken contracts', printer.HEADING_LEVEL_TWO,
                 style=printer.ERROR),
            call('Contract 1', printer.HEADING_LEVEL_THREE,
                 style=printer.ERROR),
        ])
        printer.print_error.assert_has_calls([
            call('1. foo.two imports foo.one:'),
            call('foo.two <-', bold=False),
            call('foo.one', bold=False),
        ])
        printer.print_heading.assert_has_calls([
            call('Contract 2', printer.HEADING_LEVEL_THREE,
                 style=printer.ERROR),
        ])
        printer.print_error.assert_has_calls([
            call('1. bar.two imports bar.one:'),
            call('bar.two <-', bold=False),
            call('bar.one', bold=False),
        ])
        assert self.report.has_broken_contracts is True

    def test_single_broken_contract_indirect(self, printer, make_broken_contract):
        contract = make_broken_contract(
            name='Foo',
            illegal_dependencies=[
                ('foo.four', 'foo.three', 'foo.two', 'foo.one'),
            ]
        )

        self._report_contracts([contract])

        printer.print_heading.assert_has_calls([
            call('Layer Linter', printer.HEADING_LEVEL_ONE),
            call('Contracts', printer.HEADING_LEVEL_TWO),
        ])
        printer.print_contract_one_liner.assert_has_calls([
            call(contract, is_kept=False),
        ])
        printer.print_error.assert_has_calls([call('Contracts: 0 kept, 1 broken.')])
        printer.print_heading.assert_has_calls([
            call('Broken contracts', printer.HEADING_LEVEL_TWO,
                 style=printer.ERROR),
            call('Foo', printer.HEADING_LEVEL_THREE,
                 style=printer.ERROR),
        ])
        printer.print_error.assert_has_calls([
            call('1. foo.four imports foo.one:'),
            call('foo.four <-', bold=False),
            call('foo.three <-', bold=False),
            call('foo.two <-', bold=False),
            call('foo.one', bold=False),
        ])
        assert self.report.has_broken_contracts is True

    def test_single_broken_contract_multiple_illegal_dependencies(self,
                                                                  printer, make_broken_contract):
        contract = make_broken_contract(
            name='Foo',
            illegal_dependencies=[
                ('foo.four', 'foo.three', 'foo.two', 'foo.one'),
                ('bar.two', 'bar.one'),
            ]
        )

        self._report_contracts([contract])

        printer.print_heading.assert_has_calls([
            call('Layer Linter', printer.HEADING_LEVEL_ONE),
            call('Contracts', printer.HEADING_LEVEL_TWO),
        ])
        printer.print_contract_one_liner.assert_has_calls([
            call(contract, is_kept=False),
        ])
        printer.print_error.assert_has_calls([call('Contracts: 0 kept, 1 broken.')])
        printer.print_heading.assert_has_calls([
            call('Broken contracts', printer.HEADING_LEVEL_TWO,
                 style=printer.ERROR),
            call('Foo', printer.HEADING_LEVEL_THREE,
                 style=printer.ERROR),
        ])
        printer.print_error.assert_has_calls([
            call('1. foo.four imports foo.one:'),
            call('foo.four <-', bold=False),
            call('foo.three <-', bold=False),
            call('foo.two <-', bold=False),
            call('foo.one', bold=False),
            call('2. bar.two imports bar.one:'),
            call('bar.two <-', bold=False),
            call('bar.one', bold=False),
        ])
        assert self.report.has_broken_contracts is True


@patch.object(report, 'click')
class TestConsolePrinter:
    @pytest.mark.parametrize('style,expected_color', [
        (None, None),
        (ConsolePrinter.SUCCESS, 'green',),
        (ConsolePrinter.ERROR, 'red'),
    ])
    def test_print_heading_1(self, click, style, expected_color):
        ConsolePrinter.print_heading(
            'Lorem ipsum', ConsolePrinter.HEADING_LEVEL_ONE, style)

        assert click.secho.call_count == 3
        click.secho.assert_has_calls([
            call('===========', bold=True, fg=expected_color),
            call('Lorem ipsum', bold=True, fg=expected_color),
            call('===========', bold=True, fg=expected_color),
        ])
        click.echo.assert_called_once_with()

    def test_print_heading_2(self, click):
        ConsolePrinter.print_heading(
            'Dolor sic', ConsolePrinter.HEADING_LEVEL_TWO)

        assert click.secho.call_count == 3
        click.secho.assert_has_calls([
            call('---------', bold=True, fg=None),
            call('Dolor sic', bold=True, fg=None),
            call('---------', bold=True, fg=None),
        ])
        click.echo.assert_called_once_with()

    def test_print_heading_3(self, click):
        ConsolePrinter.print_heading(
            'Amet consectetur', ConsolePrinter.HEADING_LEVEL_THREE)

        assert click.secho.call_count == 2
        click.secho.assert_has_calls([
            call('Amet consectetur', bold=True, fg=None),
            call('----------------', bold=True, fg=None),
        ])
        click.echo.assert_called_once_with()

    @pytest.mark.parametrize('bold', (True, False))
    def test_print_success(self, click, bold):
        ConsolePrinter.print_success(sentinel.text, bold)

        click.secho.assert_called_once_with(
            sentinel.text, fg='green', bold=bold)

    @pytest.mark.parametrize('bold', (True, False))
    def test_print_error(self, click, bold):
        ConsolePrinter.print_error(sentinel.text, bold)

        click.secho.assert_called_once_with(
            sentinel.text, fg='red', bold=bold)

    def test_indent_cursor(self, click):
        ConsolePrinter.indent_cursor()

        click.echo.assert_called_once_with('    ', nl=False)

    def test_new_line(self, click):
        ConsolePrinter.new_line()

        click.echo.assert_called_once_with()

    @pytest.mark.parametrize(
        'is_kept,whitelisted_path_length,expected_label,expected_color', [
            (True, 4, 'KEPT', 'green'),
            (False, 0, 'BROKEN', 'red'),
        ])
    def test_print_contract_one_liner(self, click, is_kept, whitelisted_path_length,
                                      expected_label, expected_color):
        contract = MagicMock(
            whitelisted_paths=[MagicMock()] * whitelisted_path_length
        )
        contract.__str__.return_value = 'Foo'

        ConsolePrinter.print_contract_one_liner(contract, is_kept)

        if whitelisted_path_length:
            click.secho.assert_has_calls([
                call('Foo ', nl=False),
                call('({} whitelisted paths) '.format(whitelisted_path_length), nl=False),
                call(expected_label, fg=expected_color, bold=True)
            ])
        else:
            click.secho.assert_has_calls([
                call('Foo ', nl=False),
                call(expected_label, fg=expected_color, bold=True)
            ])
