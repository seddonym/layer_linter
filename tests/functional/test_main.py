import os
import sys
from layer_linter.cmdline import main


path = os.path.join(os.path.dirname(__file__), '..', 'assets')
os.chdir(path)
sys.path.append(path)


class TestMain:
    def test_success(self):
        assert main('successpackage') == 0

    def test_failure(self):
        assert main('failurepackage') == 1
