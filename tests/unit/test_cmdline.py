from unittest.mock import patch

import pytest

from layer_linter.cmdline import _normalise_verbosity
from layer_linter.report import VERBOSITY_HIGH, VERBOSITY_NORMAL, VERBOSITY_QUIET


@pytest.mark.parametrize(
    'verbosity,is_quiet,expected_result', (
        (0, True, VERBOSITY_QUIET),
        (0, False, VERBOSITY_NORMAL),
        (1, False, VERBOSITY_HIGH),
        (1, True, "Invalid parameters: quiet and verbose called together. Choose one or the "
                  "other."),
        (2, False, "That level of verbosity is not supported. Maximum verbosity is -v."),
    )
)
def test_normalise_verbosity(verbosity, is_quiet, expected_result):
    if expected_result in (VERBOSITY_QUIET, VERBOSITY_NORMAL, VERBOSITY_HIGH):
        result = _normalise_verbosity(verbosity, is_quiet)
        assert result == expected_result
    else:
        with patch('builtins.exit') as mock_exit:
            _normalise_verbosity(verbosity, is_quiet)
            mock_exit.assert_called_once_with(expected_result)
