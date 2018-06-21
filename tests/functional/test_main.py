import os
import sys
from layer_linter.cmdline import _main


path = os.path.join(os.path.dirname(__file__), '..', 'assets')
os.chdir(path)
sys.path.append(path)


class TestMain:
    def test_success(self):
        assert _main('successpackage') == 0

    def test_failure(self):
        assert _main('failurepackage') == 1

    def test_specify_config_directory(self):
        yaml_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'yaml_directory')
        assert _main('successpackage', yaml_path) == 0
