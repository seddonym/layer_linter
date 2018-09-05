from typing import List
import argparse
import os
import sys
import logging
import importlib

from .module import SafeFilenameModule
from .dependencies import DependencyGraph
from .contract import get_contracts, Contract, ContractParseError
from .report import get_report_class, VERBOSITY_QUIET, VERBOSITY_NORMAL, VERBOSITY_HIGH


logger = logging.getLogger(__name__)


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
        '--config-directory',
        required=False,
        help="The directory containing your layers.yml. If not supplied, Layer Linter will "
             "look inside the current directory.",

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
        config_directory=args.config_directory,
        is_debug=args.is_debug,
        verbosity_count=args.verbosity_count,
        is_quiet=args.is_quiet)


def _main(package_name, config_directory=None, is_debug=False,
          verbosity_count=0, is_quiet=False):

    if is_debug:
        logging.basicConfig(level=logging.DEBUG)

    contracts = _get_contracts_or_exit(config_directory)

    package = _get_package(package_name)
    graph = DependencyGraph(package=package)

    verbosity = _normalise_verbosity(verbosity_count, is_quiet)
    report_class = get_report_class(verbosity)
    report = report_class(graph)

    for contract in contracts:
        contract.check_dependencies(graph)
        report.add_contract(contract)

    report.output()

    if report.has_broken_contracts:
        return 1  # Fail
    else:
        return 0  # Pass


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
            exit("Invalid parameters: quiet and verbose called together. Choose one or the other.")
        return VERBOSITY_QUIET

    try:
        return VERBOSITY_BY_COUNT[verbosity_count]
    except IndexError:
        exit("That level of verbosity is not supported. Maximum verbosity is -{}.".format(
             'v' * (len(VERBOSITY_BY_COUNT) - 1)))


def _get_package(package_name: str) -> SafeFilenameModule:
    """
    Get the package as a SafeFilenameModule.
    """
    # Add current directory to the path, as this doesn't happen automatically.
    sys.path.insert(0, os.getcwd())

    # Attempt to locate the package file.
    package_filename = importlib.util.find_spec(package_name)
    if not package_filename:
        logger.debug("sys.path: {}".format(sys.path))
        exit("Could not find package '{}' in your path.".format(package_name))
    assert package_filename.origin  # For type checker.
    return SafeFilenameModule(name=package_name, filename=package_filename.origin)


def _get_contracts_or_exit(config_directory: str) -> List[Contract]:
    # Parse contracts file.
    if config_directory is None:
        config_directory = os.getcwd()
    try:
        return get_contracts(path=config_directory)
    except FileNotFoundError as e:
        exit("{}: {}".format(e.strerror, e.filename))
    except ContractParseError as e:
        exit('Error: {}'.format(e))
