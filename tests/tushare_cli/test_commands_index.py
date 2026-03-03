import pandas as pd
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from tushare_cli.main import cli

MOCK_DF = pd.DataFrame({"ts_code": ["000300.SH"], "close": [3500.0]})


def run_cmd(args):
    pro = MagicMock()
    for m in ["index_global", "sw_daily", "index_classify", "index_member_all"]:
        getattr(pro, m).return_value = MOCK_DF
    runner = CliRunner()
    with patch("tushare.pro_api", return_value=pro):
        with patch("tushare_cli.api.resolve_token", return_value="fake"):
            return runner.invoke(cli, args)


def test_index_global():
    result = run_cmd(["index", "global", "--index-code", "SPX"])
    assert result.exit_code == 0

def test_index_sw_daily():
    result = run_cmd(["index", "sw-daily", "--ts-code", "801010.SI"])
    assert result.exit_code == 0

def test_index_classify():
    result = run_cmd(["index", "classify", "--level", "L1"])
    assert result.exit_code == 0

def test_index_sw_members():
    result = run_cmd(["index", "sw-members", "--l1-code", "801010.SI"])
    assert result.exit_code == 0
