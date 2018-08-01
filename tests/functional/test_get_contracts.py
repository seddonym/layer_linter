import os

from layer_linter.contract import get_contracts, Layer
from layer_linter.dependencies import ImportPath


def test_get_contracts():
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, '..', 'assets', 'singlecontractfile')

    contracts = get_contracts(path)

    assert len(contracts) == 2
    expected_contracts = [
        {
            'name': 'Contract A',
            'packages': ['foo', 'bar'],
            'layers': ['one', 'two'],
        },
        {
            'name': 'Contract B',
            'packages': ['baz/*'],
            'layers': ['one', 'two', 'three'],
            'whitelisted_paths': [
                ('baz.utils', 'baz.three.green'),
                ('baz.three.blue', 'baz.two'),
            ],
        },
    ]
    sorted_contracts = sorted(contracts, key=lambda i: i.name)
    for contract_index, contract in enumerate(sorted_contracts):
        expected_data = expected_contracts[contract_index]
        assert contract.name == expected_data['name']

        for package_index, package in enumerate(contract.packages):
            expected_package_data = expected_data['packages'][package_index]
            assert package == expected_package_data

        for layer_index, layer in enumerate(contract.layers):
            expected_layer_data = expected_data['layers'][layer_index]
            assert isinstance(layer, Layer)
            assert layer.name == expected_layer_data

        for whitelisted_index, whitelisted_path in enumerate(contract.whitelisted_paths):
            expected_importer, expected_imported = expected_data['whitelisted_paths'][
                whitelisted_index]
            assert isinstance(whitelisted_path, ImportPath)
            assert whitelisted_path.importer == expected_importer
            assert whitelisted_path.imported == expected_imported
