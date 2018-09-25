import os
import sys

from layer_linter.cmdline import _main
from layer_linter.report import VERBOSITY_QUIET, VERBOSITY_NORMAL, VERBOSITY_HIGH

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
        path = os.path.join(assets_path, 'successpackage')
        os.chdir(path)
        sys.path.append(path)

        result = _main('successpackage', verbosity_count=verbosity_count, is_quiet=is_quiet)

        if should_always_fail:
            assert result == 1
        else:
            assert result == 0

    def test_failure(self, verbosity_count, is_quiet, should_always_fail):
        path = os.path.join(assets_path, 'failurepackage')
        os.chdir(path)
        sys.path.append(path)

        result = _main('failurepackage', verbosity_count=verbosity_count, is_quiet=is_quiet)
        assert result == 1

    def test_specify_config_file(self, verbosity_count, is_quiet, should_always_fail):
        path = os.path.join(assets_path, 'successpackage')
        os.chdir(path)
        sys.path.append(path)


        result = _main(
            'successpackage',
            config_filename='layers_alternative.yml',
            verbosity_count=verbosity_count,
            is_quiet=is_quiet)

        if should_always_fail:
            assert result == 1
        else:
            assert result == 0
