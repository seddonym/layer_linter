import click


class ContractAdherenceReport:
    def __init__(self, dependencies):
        self.dependencies = dependencies
        self.kept_contracts = []
        self.broken_contracts = []
        self.has_broken_contracts = False

    def add_contract(self, contract):
        if contract.is_kept:
            self.kept_contracts.append(contract)
        else:
            self.broken_contracts.append(contract)
            self.has_broken_contracts = True

    def output(self):
        ConsolePrinter.print_heading('Layer Linter', ConsolePrinter.HEADING_LEVEL_ONE)
        ConsolePrinter.print_heading('Contracts', ConsolePrinter.HEADING_LEVEL_TWO)

        ConsolePrinter.print_heading(
            'Analyzed {} files, {} dependencies.'.format(
                self.dependencies.module_count,
                self.dependencies.dependency_count,
            ), ConsolePrinter.HEADING_LEVEL_THREE)

        if not (self.kept_contracts or self.broken_contracts):
            ConsolePrinter.print_error('No contracts found.')

        for contract in self.kept_contracts:
            ConsolePrinter.print_contract_one_liner(contract, is_kept=True)

        for contract in self.broken_contracts:
            ConsolePrinter.print_contract_one_liner(contract, is_kept=False)

        ConsolePrinter.new_line()

        # Print summary line.
        print_callback = ConsolePrinter.print_error if self.broken_contracts else \
            ConsolePrinter.print_success
        print_callback('Contracts: {} kept, {} broken.'.format(
            len(self.kept_contracts),
            len(self.broken_contracts)
        ))
        ConsolePrinter.new_line()

        if self.broken_contracts:
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


class InvalidDependenciesReport:
    def __init__(self, exception):
        self.exception = exception

    def output(self):
        ...


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
    def print_contract_one_liner(cls, contract, is_kept):
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
