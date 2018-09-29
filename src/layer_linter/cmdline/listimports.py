import argparse
import logging

from layer_linter.importanalysis import ImportAnalysis
from layer_linter.listimportreport import ImportsReport
from layer_linter.module import Module


logger = logging.getLogger(__name__)

def create_parser():
    parser = argparse.ArgumentParser(
        description='Lists all the modules inside your project that the given module imports.'
    )

    parser.add_argument(
        'module_name',
        help='The name of the Python module whose imports to list.'
    )

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    return _main(
        module_name=args.module_name,
    )


def _main(module_name: str) -> None:
    module = Module(module_name)

    analysis = ImportAnalysis(module)

    report = ImportsReport(analysis)
    report.output()
