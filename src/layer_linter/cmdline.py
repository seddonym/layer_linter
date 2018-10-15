from typing import List
import argparse
import os
import sys
import logging
import importlib

from .module import SafeFilenameModule
from .dependencies import DependencyGraph
from .contract import get_contracts, Contract, ContractParseError
from .report import (
    get_report_class, ConsolePrinter, VERBOSITY_QUIET, VERBOSITY_NORMAL, VERBOSITY_HIGH)


logger = logging.getLogger(__name__)

EXIT_STATUS_SUCCESS = 0
EXIT_STATUS_ERROR = 1

def create_parser():
    parser = argparse.ArgumentParser(
        description='Checks that your project follows a custom-defined '
        'layered architecture, based on a layers.yml file.'
    )

    parser.add_argument(
        'package_name',
        help='The name of the Python package to validate.'
    )

    parser.add_argument(
        '--config',
        required=False,
        help="The YAML file describing your contract(s). If not supplied, Layer Linter will "
             "look for a file called 'layers.yml' inside the current directory.",

    )

    parser.add_argument(
        '-v',
        '--verbose',
        # Using a count allows us to increase verbosity levels using -vv, -vvv etc., should they
        # be necessary in future.
        action='count',
        default=0,
        dest='verbosity_count',
        help="Increase verbosity."
    )

    parser.add_argument(
        '--quiet',
        required=False,
        action='store_true',
        dest='is_quiet',
        help="Do not output anything on success."
    )

    parser.add_argument(
        '--debug',
        required=False,
        action="store_true",
        dest='is_debug',
        help="Whether to display debug information.",
    )

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    return _main(
        package_name=args.package_name,
        config_filename=args.config,
        is_debug=args.is_debug,
        verbosity_count=args.verbosity_count,
        is_quiet=args.is_quiet)


def _main(package_name, config_filename=None, is_debug=False,
          verbosity_count=0, is_quiet=False):

    if is_debug:
        logging.basicConfig(level=logging.DEBUG)

    try:
        contracts = _get_contracts(config_filename)
    except Exception as e:
        ConsolePrinter.print_error(str(e))
        return EXIT_STATUS_ERROR

    try:
        package = _get_package(package_name)
    except ValueError as e:
        _print_package_name_error_and_help(str(e))
        return EXIT_STATUS_ERROR

    graph = DependencyGraph(package=package)

    try:
        verbosity = _normalise_verbosity(verbosity_count, is_quiet)
    except Exception as e:
        ConsolePrinter.print_error(str(e))
        return EXIT_STATUS_ERROR

    report_class = get_report_class(verbosity)
    report = report_class(graph)

    for contract in contracts:
        contract.check_dependencies(graph)
        report.add_contract(contract)

    report.output()

    if report.has_broken_contracts:
        return EXIT_STATUS_ERROR
    else:
        return EXIT_STATUS_SUCCESS


def _normalise_verbosity(verbosity_count: int, is_quiet: bool) -> int:
    """
    Validate verbosity, and parse quiet mode into a verbosity level.

    Args:
        verbosity_count (int): the number of 'v's passed as command line arguments. For example,
                               -vv would be 2.
        is_quiet (bool):       whether the '--quiet' flag was passed.

    Returns:
        Verbosity level (int): either VERBOSITY_QUIET, VERBOSITY_NORMAL or VERBOSITY_HIGH.
    """
    VERBOSITY_BY_COUNT = (VERBOSITY_NORMAL, VERBOSITY_HIGH)

    if is_quiet:
        if verbosity_count > 0:
            raise RuntimeError(
                "Invalid parameters: quiet and verbose called together. Choose one or the other.")
        return VERBOSITY_QUIET

    try:
        return VERBOSITY_BY_COUNT[verbosity_count]
    except IndexError:
        raise RuntimeError(
            "That level of verbosity is not supported. "
            "Maximum verbosity is -{}.".format('v' * (len(VERBOSITY_BY_COUNT) - 1)))


def _get_package(package_name: str) -> SafeFilenameModule:
    """
    Get the package as a SafeFilenameModule.

    Raises ValueError, with appropriate user-facing message, if the package name is
    not valid.
    """
    if '.' in package_name:
        raise ValueError("Package name must be the root name, no '.' allowed.")
    if ('/' in package_name) or ('\\' in package_name):
        raise ValueError("The package name should not be a directory, it should be the name of "
                         "the importable Python package.")

    # Add current directory to the path, as this doesn't happen automatically.
    sys.path.insert(0, os.getcwd())

    # Attempt to locate the package file.
    package_filename = importlib.util.find_spec(package_name)
    if not package_filename:
        logger.debug("sys.path: {}".format(sys.path))
        raise ValueError("Could not find package '{}' in your Python path.".format(package_name))
    assert package_filename.origin  # For type checker.
    return SafeFilenameModule(name=package_name, filename=package_filename.origin)


def _get_contracts(config_filename: str) -> List[Contract]:
    # Parse contracts file.
    if config_filename is None:
        config_filename = os.path.join(os.getcwd(), 'layers.yml')
    try:
        return get_contracts(filename=config_filename)
    except FileNotFoundError as e:
        raise RuntimeError("{}: {}".format(e.strerror, e.filename))
    except ContractParseError as e:
        raise RuntimeError('Error parsing contract: {}'.format(e))


def _print_package_name_error_and_help(error_text):
    ConsolePrinter.print_heading('Invalid package name',
                                 ConsolePrinter.HEADING_LEVEL_TWO,
                                 ConsolePrinter.ERROR)
    ConsolePrinter.print_error(error_text)
    ConsolePrinter.new_line()
    ConsolePrinter.print_heading('Tip', ConsolePrinter.HEADING_LEVEL_THREE,
                                 ConsolePrinter.ERROR)
    ConsolePrinter.print_error('Your package should either be in the current working directory, ')
    ConsolePrinter.print_error('or installed (e.g. in your virtual environment).')
    ConsolePrinter.new_line()
    ConsolePrinter.print_error('If your package has a setup.py, the easiest way to install it is ')
    ConsolePrinter.print_error('to run the following command, which installs it, while keeping ')
    ConsolePrinter.print_error('it editable:')
    ConsolePrinter.new_line()
    ConsolePrinter.indent_cursor()
    ConsolePrinter.print_error('pip install -e path/to/setup.py')
    ConsolePrinter.new_line()
    ConsolePrinter.print_error("Alternatively, you may run Layer Linter from the directory that ")
    ConsolePrinter.print_error("contains your package directory. If your layers.yml is located ")
    ConsolePrinter.print_error("elsewhere, you may specify its file path using the config flag. ")
    ConsolePrinter.print_error("For example:")
    ConsolePrinter.new_line()
    ConsolePrinter.indent_cursor()
    ConsolePrinter.print_error(
        'layer-lint mypackage --config path/to/layers.yml')
    ConsolePrinter.new_line()
