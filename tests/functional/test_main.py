import os
import sys

from layer_linter.cmdline import _main
from layer_linter.report import VERBOSITY_QUIET, VERBOSITY_NORMAL, VERBOSITY_HIGH

import pytest

assets_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets'))


@pytest.mark.parametrize(
    'verbosity', (VERBOSITY_QUIET, VERBOSITY_NORMAL, VERBOSITY_HIGH)
)
class TestMain:
    def test_success(self, verbosity):
        path = os.path.join(assets_path, 'successpackage')
        os.chdir(path)
        sys.path.append(path)

        assert _main('successpackage', verbosity=verbosity) == 0

    def test_failure(self, verbosity):
        path = os.path.join(assets_path, 'failurepackage')
        os.chdir(path)
        sys.path.append(path)

        assert _main('failurepackage', verbosity=verbosity) == 1

    def test_specify_config_directory(self, verbosity):
        path = os.path.join(assets_path, 'successpackage')
        os.chdir(path)
        sys.path.append(path)
        yaml_path = os.path.join(os.path.dirname(__file__),
                                 '..', 'assets', 'yaml_directory')
        assert _main('successpackage', yaml_path, verbosity=verbosity) == 0
