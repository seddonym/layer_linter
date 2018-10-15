import os
import sys

import pytest

from layer_linter.contract import get_contracts, Layer
from layer_linter.dependencies import ImportPath
from layer_linter.module import Module


class TestGetContracts:
    def test_happy_path(self):
        self._initialize_test()

        contracts = get_contracts(self.filename_and_path, package_name='singlecontractfile')

        assert len(contracts) == 2
        expected_contracts = [
            {
                'name': 'Contract A',
                'packages': ['singlecontractfile.foo', 'singlecontractfile.bar'],
                'layers': ['one', 'two'],
            },
            {
                'name': 'Contract B',
                'packages': ['singlecontractfile'],
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

            for package_index, package in enumerate(contract.containers):
                expected_package_name = expected_data['packages'][package_index]
                assert package == Module(expected_package_name)

            for layer_index, layer in enumerate(contract.layers):
                expected_layer_data = expected_data['layers'][layer_index]
                assert isinstance(layer, Layer)
                assert layer.name == expected_layer_data

            for whitelisted_index, whitelisted_path in enumerate(contract.whitelisted_paths):
                expected_importer, expected_imported = expected_data['whitelisted_paths'][
                    whitelisted_index]
                assert isinstance(whitelisted_path, ImportPath)
                assert whitelisted_path.importer == Module(expected_importer)
                assert whitelisted_path.imported == Module(expected_imported)

    def test_container_does_not_exist(self):
        self._initialize_test('layers_with_missing_container.yml')

        with pytest.raises(ValueError) as e:
            get_contracts(self.filename_and_path, package_name='singlecontractfile')

        assert str(e.value) == "Invalid container 'singlecontractfile.missing': no such package."

    def _initialize_test(self, config_filename='layers.yml'):
        # Append the package directory to the path.
        dirname = os.path.dirname(__file__)
        package_dirname = os.path.join(dirname, '..', 'assets', 'singlecontractfile')
        sys.path.append(package_dirname)

        # Set the full config filename and path as an instance attribute.
        self.filename_and_path = os.path.join(package_dirname, config_filename)
