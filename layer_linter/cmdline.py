import os
import sys
import logging

from .dependencies import get_dependencies
from .contract import get_contracts
from .report import Report

logger = logging.getLogger('dependencycheck')
logging.getLogger('pydeps').setLevel(logging.ERROR)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def main():
    dependencies = get_dependencies('layers')  # TODO get from cmd line
    report = Report()
    for contract in get_contracts(path=os.path.join(os.getcwd(), 'layers')):
        contract.check_dependencies(dependencies)
        report.add_contract(contract)

    report.output()

    if report.has_broken_contracts:
        return 1  # Fail
    else:
        return 0  # Pass
