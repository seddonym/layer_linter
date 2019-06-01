import os
from typing import Tuple, List

from layer_linter.dependencies.scanner import PackageScanner
from layer_linter.module import SafeFilenameModule


class TestPackageScanner:
    def test_success(self):
        package = SafeFilenameModule(
            name='scannersuccess',
            filename=os.path.join(self._get_package_directory('scannersuccess'), '__init__.py'),
        )

        scanner = PackageScanner(package)
        modules = scanner.scan_for_modules()

        expected_modules = self._build_modules(
            package_name='scannersuccess',
            tuples=(
                ('scannersuccess', '__init__.py'),
                ('scannersuccess.one', os.path.join('one', '__init__.py')),
                ('scannersuccess.one.alpha', os.path.join('one', 'alpha.py')),
                ('scannersuccess.one.beta', os.path.join('one', 'beta.py')),
                ('scannersuccess.one.gamma', os.path.join('one', 'gamma.py')),
                ('scannersuccess.one.delta', os.path.join('one', 'delta', '__init__.py')),
                ('scannersuccess.one.delta.green', os.path.join('one', 'delta', 'green.py')),
                ('scannersuccess.one.delta.red_blue', os.path.join('one', 'delta', 'red_blue.py')),
                ('scannersuccess.two', os.path.join('two', '__init__.py')),
                ('scannersuccess.two.alpha', os.path.join('two', 'alpha.py')),
                ('scannersuccess.two.beta', os.path.join('two', 'beta.py')),
                ('scannersuccess.two.gamma', os.path.join('two', 'gamma.py')),
                ('scannersuccess.four', 'four.py'),
                # Also include invalid modules. To keep things simple, Layer Linter won't decide
                # what is and isn't allowed - but we don't want them to break things.
                ('scannersuccess.in', os.path.join('in', '__init__.py')),
                ('scannersuccess.in.class', os.path.join('in', 'class.py')),
                ('scannersuccess.in.hyphenated-name', os.path.join('in', 'hyphenated-name.py')),

            ),
        )
        assert set(modules) == set(expected_modules)
        # Also check that the filenames are the same.
        sorted_modules = sorted(modules, key=lambda m: m.name)
        sorted_expected_modules = sorted(expected_modules, key=lambda m: m.name)
        for index, module in enumerate(sorted_modules):
            assert module.filename == sorted_expected_modules[index].filename

    def _get_package_directory(self, package_name: str) -> str:
        """
        Return absolute path to the package directory.
        """
        return os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                '..', '..', 'assets', package_name, package_name,
            )
        )

    def _build_modules(self,
                       package_name: str,
                       tuples: Tuple[Tuple[str, str]]) -> List[SafeFilenameModule]:
        package_directory = self._get_package_directory(package_name)
        modules = []
        for module_name, module_filename in tuples:
            modules.append(
                SafeFilenameModule(
                    name=module_name,
                    filename=os.path.join(package_directory, module_filename),
                )
            )
        return modules
