from unittest.mock import patch

import pytest

from layer_linter import cmdline
from layer_linter.cmdline import _normalise_verbosity, _main
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
        with pytest.raises(RuntimeError) as e:
            _normalise_verbosity(verbosity, is_quiet)
        assert str(e.value) == expected_result


@pytest.mark.parametrize(
    'is_debug', (True, False)
)
@patch.object(cmdline, 'get_report_class')
@patch.object(cmdline, 'DependencyGraph')
@patch.object(cmdline, '_get_package')
@patch.object(cmdline, '_get_contracts')
@patch.object(cmdline, 'logging')
def test_debug(mock_logging, mock_get_contracts, mock_get_package, mock_graph,
               mock_get_report_class, is_debug):

    _main('foo', is_debug=is_debug)

    if is_debug:
        mock_logging.basicConfig.assert_called_once_with(level=mock_logging.DEBUG)
    else:
        mock_logging.basicConfig.assert_not_called()
