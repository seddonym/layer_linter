import os
import sys

import pytest

from layer_linter.dependencies.scanner import PackageScanner
from layer_linter.module import Module


class TestPackageScanner:
    def test_success(self):
        dirname = os.path.dirname(__file__)
        path = os.path.abspath(os.path.join(dirname, '..', '..', 'assets', 'scannersuccess'))

        sys.path.append(path)

        package = __import__('scannersuccess')

        scanner = PackageScanner(package)

        expected_modules = map(Module, [
            'scannersuccess',
            'scannersuccess.one',
            'scannersuccess.one.alpha',
            'scannersuccess.one.beta',
            'scannersuccess.one.gamma',
            'scannersuccess.one.delta',
            'scannersuccess.one.delta.green',
            'scannersuccess.one.delta.red_blue',
            'scannersuccess.two',
            'scannersuccess.two.alpha',
            'scannersuccess.two.beta',
            'scannersuccess.two.gamma',
            'scannersuccess.four',
        ])

        modules = scanner.scan_for_modules()

        assert set(modules) == set(expected_modules)

    def test_invalid_modules(self):
        dirname = os.path.dirname(__file__)
        path = os.path.abspath(os.path.join(dirname, '..', '..', 'assets', 'scannerinvalid'))

        sys.path.append(path)

        package = __import__('scannerinvalid')

        expected_illegal_module_filenames = map(
            lambda p: os.path.join(path, p),
            [
                'scannerinvalid/one/in/__init__.py',
                'scannerinvalid/one/in/green.py',
                'scannerinvalid/one/class.py',
                'scannerinvalid/two/123.py',
                'scannerinvalid/two/hyphenated-name.py',
            ]
        )

        scanner = PackageScanner(package)
        scanner.scan_for_modules()

        assert set(scanner.illegal_module_filenames) == set(expected_illegal_module_filenames)
