import pandas as pd
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from tushare_cli.main import cli

MOCK_DF = pd.DataFrame({"ts_code": ["IF2403.CFX"], "close": [3800.0]})


def run_cmd(args):
    pro = MagicMock()
    for m in ["fut_basic", "index_daily", "fut_holding", "fut_wsr",
              "rt_fut_min", "rt_fut_min_daily"]:
        getattr(pro, m).return_value = MOCK_DF
    runner = CliRunner()
    with patch("tushare.pro_api", return_value=pro):
        with patch("tushare_cli.api.resolve_token", return_value="fake"):
            return runner.invoke(cli, args)


def test_futures_contracts():
    result = run_cmd(["futures", "contracts", "--exchange", "CFFEX"])
    assert result.exit_code == 0

def test_futures_nh_index():
    result = run_cmd(["futures", "nh-index", "--ts-code", "NH0100.NH"])
    assert result.exit_code == 0

def test_futures_holdings():
    result = run_cmd(["futures", "holdings", "--trade-date", "20240101"])
    assert result.exit_code == 0

def test_futures_wsr():
    result = run_cmd(["futures", "wsr", "--trade-date", "20240101"])
    assert result.exit_code == 0

def test_futures_minute():
    result = run_cmd(["futures", "minute", "--ts-code", "IF2403.CFX", "--freq", "15MIN"])
    assert result.exit_code == 0
