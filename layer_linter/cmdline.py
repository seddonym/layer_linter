import argparse
import os
import logging

from .dependencies import get_dependencies
from .contract import get_contracts, ContractParseError
from .report import Report


def create_parser():
    parser = argparse.ArgumentParser(
        description='Checks that your project follows a custom-defined '
        'layered architecture, based on a layers.yaml file.'
    )

    parser.add_argument(
        'package_name',
        help='The name of the Python package to validate.'
    )

    parser.add_argument(
        '--config-directory',
        required=False,
        help="The directory containing your layers.yaml. If not supplied, Layer Linter will "
             "look inside the current directory.",

    )
    parser.add_argument(
        '--debug',
        required=False,
        action="store_true",
        help="Whether to display debug information.",
    )

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    return _main(args.package_name, args.config_directory, args.debug)


def _main(package_name, config_directory=None, is_debug=False):
    if is_debug:
        logging.basicConfig(level=logging.DEBUG)

    try:
        package = __import__(package_name)
    except ImportError:
        exit("Could not find package '{}' in your path.".format(package_name))

    if config_directory is None:
        config_directory = os.getcwd()
    try:
        contracts = get_contracts(path=config_directory)
    except FileNotFoundError as e:
        exit("{}: {}".format(e.strerror, e.filename))
    except ContractParseError as e:
        exit('Error: {}'.format(e))

    dependencies = get_dependencies(package)

    report = Report(dependencies)
    for contract in contracts:
        contract.check_dependencies(dependencies)
        report.add_contract(contract)
    report.output()

    if report.has_broken_contracts:
        return 1  # Fail
    else:
        return 0  # Pass
