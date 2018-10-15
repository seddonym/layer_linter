import os
import sys

from layer_linter.cmdline import _main, EXIT_STATUS_SUCCESS, EXIT_STATUS_ERROR

import pytest

assets_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets'))


@pytest.mark.parametrize(
    'verbosity_count, is_quiet, should_always_fail',
    (
        (0, False, False),  # no args
        (0, True, False),  # --quiet
        (1, False, False),  # -v
        (1, True, True),  # -v --quiet: should always fail.
    )
)
class TestMain:
    def test_success(self, verbosity_count, is_quiet, should_always_fail):
        package_name = 'successpackage'
        self._chdir_and_add_to_system_path(package_name)

        result = _main(package_name, verbosity_count=verbosity_count, is_quiet=is_quiet)

        if should_always_fail:
            assert result == EXIT_STATUS_ERROR
        else:
            assert result == EXIT_STATUS_SUCCESS

    def test_failure(self, verbosity_count, is_quiet, should_always_fail):
        package_name = 'failurepackage'
        self._chdir_and_add_to_system_path(package_name)

        result = _main(package_name, verbosity_count=verbosity_count, is_quiet=is_quiet)

        assert result == EXIT_STATUS_ERROR

    def test_specify_config_file(self, verbosity_count, is_quiet, should_always_fail):
        package_name = 'successpackage'
        self._chdir_and_add_to_system_path(package_name)

        result = _main(
            package_name,
            config_filename='layers_alternative.yml',
            verbosity_count=verbosity_count,
            is_quiet=is_quiet)

        if should_always_fail:
            assert result == EXIT_STATUS_ERROR
        else:
            assert result == EXIT_STATUS_SUCCESS

    def _chdir_and_add_to_system_path(self, package_name):
        path = os.path.join(assets_path, package_name)
        sys.path.append(path)
        os.chdir(path)
