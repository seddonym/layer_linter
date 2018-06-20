from .dependencies import get_dependencies
from .contract import get_contracts
from .report import Report


def main(package_name):

    try:
        package = __import__(package_name)
    except ImportError:
        exit("Could not find package '{}' in your path.".format(package_name))

    dependencies = get_dependencies(package.__name__)

    report = Report()
    for contract in get_contracts(path=package.__path__[0]):
        contract.check_dependencies(dependencies)
        report.add_contract(contract)

    report.output()

    if report.has_broken_contracts:
        return 1  # Fail
    else:
        return 0  # Pass
