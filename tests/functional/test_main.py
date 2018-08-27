import os
import sys
from layer_linter.cmdline import _main

import pytest

assets_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets'))


class TestMain:
    def test_success(self):
        path = os.path.join(assets_path, 'successpackage')
        os.chdir(path)
        sys.path.append(path)

        assert _main('successpackage') == 0

    def test_failure(self):
        path = os.path.join(assets_path, 'failurepackage')
        os.chdir(path)
        sys.path.append(path)

        assert _main('failurepackage') == 1

    def test_specify_config_directory(self):
        path = os.path.join(assets_path, 'successpackage')
        os.chdir(path)
        sys.path.append(path)
        yaml_path = os.path.join(os.path.dirname(__file__),
                                 '..', 'assets', 'yaml_directory')
        assert _main('successpackage', yaml_path) == 0
