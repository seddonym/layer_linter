from typing import List, Type

import click

from .dependencies import DependencyGraph
from .contract import Contract

VERBOSITY_QUIET = 0
VERBOSITY_NORMAL = 1
VERBOSITY_HIGH = 2


def get_report_class(verbosity: int) -> Type['BaseReport']:
    return {
        VERBOSITY_QUIET: QuietReport,
        VERBOSITY_NORMAL: NormalReport,
        VERBOSITY_HIGH: VerboseReport,
    }[verbosity]


class BaseReport:
    def __init__(self, graph: DependencyGraph) -> None:
        self.graph = graph
        self.kept_contracts: List[Contract] = []
        self.broken_contracts: List[Contract] = []
        self.has_broken_contracts = False

    def add_contract(self, contract: Contract) -> None:
        if contract.is_kept:
            self.kept_contracts.append(contract)
        else:
            self.broken_contracts.append(contract)
            self.has_broken_contracts = True

    def output(self) -> None:
        self._output_title()
        self._output_contracts_analysis()
        if self.broken_contracts:
            self._output_broken_contracts_details()

    def _output_title(self):
        ConsolePrinter.print_heading('Layer Linter', ConsolePrinter.HEADING_LEVEL_ONE)

    def _output_contracts_analysis(self):
        ConsolePrinter.print_heading('Contracts', ConsolePrinter.HEADING_LEVEL_TWO)

        ConsolePrinter.print_heading(
            'Analyzed {} files, {} dependencies.'.format(
                self.graph.module_count,
                self.graph.dependency_count,
            ), ConsolePrinter.HEADING_LEVEL_THREE)

        for contract in self.kept_contracts:
            self._output_contract_analysis(contract)

        for contract in self.broken_contracts:
            self._output_contract_analysis(contract)

        self._output_contracts_summary()

    def _output_contract_analysis(self, contract):
        ConsolePrinter.print_contract_one_liner(contract)

    def _output_contracts_summary(self):
        # Print summary line.
        ConsolePrinter.new_line()
        print_callback = ConsolePrinter.print_error if self.broken_contracts else \
            ConsolePrinter.print_success
        print_callback('Contracts: {} kept, {} broken.'.format(
            len(self.kept_contracts),
            len(self.broken_contracts)
        ))
        ConsolePrinter.new_line()

    def _output_broken_contracts_details(self):
        ConsolePrinter.print_heading('Broken contracts', ConsolePrinter.HEADING_LEVEL_TWO,
                                                         style=ConsolePrinter.ERROR)
        ConsolePrinter.new_line()

        for broken_contract in self.broken_contracts:
            ConsolePrinter.print_heading(str(broken_contract), ConsolePrinter.HEADING_LEVEL_THREE,
                                         style=ConsolePrinter.ERROR)

            ConsolePrinter.new_line()

            for index, illegal_dependency in enumerate(broken_contract.illegal_dependencies):
                first = illegal_dependency[0]
                last = illegal_dependency[-1]

                ConsolePrinter.print_error('{}. {} imports {}:'.format(index + 1, first, last))
                ConsolePrinter.new_line()

                for dep_index, item in enumerate(illegal_dependency):
                    error_text = str(item)
                    if dep_index < len(illegal_dependency) - 1:
                        error_text += ' <-'
                    ConsolePrinter.indent_cursor()
                    ConsolePrinter.print_error(error_text, bold=False)
                ConsolePrinter.new_line()


class NormalReport(BaseReport):
    pass


class QuietReport(NormalReport):
    """
    Report that only reports when there is a broken contract.
    """
    def output(self) -> None:
        if self.broken_contracts:
           super().output()


class VerboseReport(BaseReport):
    def output(self):
        self._output_title()
        self._output_dependencies()
        self._output_contracts_analysis()
        if self.broken_contracts:
            self._output_broken_contracts_details()

    def _output_dependencies(self):
        ConsolePrinter.print_heading('Dependencies', ConsolePrinter.HEADING_LEVEL_TWO)

        for importer in self.graph.modules:
            ConsolePrinter.print('{} imports:'.format(importer), bold=True)
            has_at_least_one_successor = False
            for imported in self.graph.get_modules_directly_imported_by(importer=importer):
                has_at_least_one_successor = True
                ConsolePrinter.indent_cursor()
                ConsolePrinter.print('- {}'.format(imported))
            if not has_at_least_one_successor:
                ConsolePrinter.indent_cursor()
                ConsolePrinter.print('- (nothing)')
        ConsolePrinter.new_line()


class ConsolePrinter:
    ERROR = 'error'
    SUCCESS = 'success'
    COLORS = {
        ERROR: 'red',
        SUCCESS: 'green',
    }

    HEADING_LEVEL_ONE = 1
    HEADING_LEVEL_TWO = 2
    HEADING_LEVEL_THREE = 3

    HEADING_MAP = {
        HEADING_LEVEL_ONE: ('=', True),
        HEADING_LEVEL_TWO: ('-', True),
        HEADING_LEVEL_THREE: ('-', False),
    }

    INDENT_SIZE = 4

    @classmethod
    def print_heading(cls, text, level, style=None):
        """
        Prints the supplied text to the console, formatted as a heading.

        Args:
            text (str): the text to format as a heading.
            level (int): the level of heading to display (one of the keys of HEADING_MAP).
            style (str, optional): ERROR or SUCCESS style to apply (default None).
        Usage:

            ConsolePrinter.print_heading('Foo', ConsolePrinter.HEADING_LEVEL_ONE)
        """
        # Setup styling variables.
        is_bold = True
        color = cls.COLORS[style] if style else None
        line_char, show_line_above = cls.HEADING_MAP[level]
        heading_line = line_char * len(text)

        # Print lines.
        if show_line_above:
            click.secho(heading_line, bold=is_bold, fg=color)
        click.secho(text, bold=is_bold, fg=color)
        click.secho(heading_line, bold=is_bold, fg=color)
        click.echo()

    @classmethod
    def print(cls, text, bold=False):
        """
        Prints a line to the console.
        """
        click.secho(text, bold=bold)

    @classmethod
    def print_success(cls, text, bold=True):
        """
        Prints a line to the console, formatted as a success.
        """
        click.secho(text, fg=cls.COLORS[cls.SUCCESS], bold=bold)

    @classmethod
    def print_error(cls, text, bold=True):
        """
        Prints a line to the console, formatted as an error.
        """
        click.secho(text, fg=cls.COLORS[cls.ERROR], bold=bold)

    @classmethod
    def indent_cursor(cls):
        """
        Indents the cursor ready to print a line.
        """
        click.echo(' ' * cls.INDENT_SIZE, nl=False)

    @classmethod
    def new_line(cls):
        click.echo()

    @classmethod
    def print_contract_one_liner(cls, contract: Contract) -> None:
        is_kept = contract.is_kept
        click.secho('{} '.format(contract), nl=False)
        if contract.whitelisted_paths:
            click.secho('({} whitelisted paths) '.format(len(contract.whitelisted_paths)),
                        nl=False)
        status_map = {
            True: ('KEPT', cls.SUCCESS),
            False: ('BROKEN', cls.ERROR),
        }
        color = cls.COLORS[status_map[is_kept][1]]
        click.secho(status_map[is_kept][0], fg=color, bold=True)
