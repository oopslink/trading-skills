import pandas as pd
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from tushare_cli.main import cli

MOCK_DF = pd.DataFrame({"ts_code": ["USDCNH.FX"], "close": [7.2]})


def run_cmd(args, module=None):
    pro = MagicMock()
    for m in ["fx_daily", "income", "fina_indicator",
              "dc_index", "dc_member", "dc_daily", "moneyflow_ind_dc",
              "rt_k", "sw_daily", "index_classify"]:
        getattr(pro, m).return_value = MOCK_DF
    runner = CliRunner()
    patches = [patch("tushare.pro_api", return_value=pro)]
    if module:
        patches.append(patch(f"tushare_cli.commands.{module}.resolve_token", return_value="fake"))
    from contextlib import ExitStack
    with ExitStack() as stack:
        for p in patches:
            stack.enter_context(p)
        return runner.invoke(cli, args)


# Forex
def test_forex_daily():
    result = run_cmd(["forex", "daily", "--symbol", "USDCNH"], module="forex")
    assert result.exit_code == 0

def test_forex_daily_auto_suffix():
    result = run_cmd(["forex", "daily", "--symbol", "USDCNH.FX"], module="forex")
    assert result.exit_code == 0

# Financial
def test_financial_income():
    result = run_cmd(["financial", "income", "--ts-code", "000001.SZ"], module="financial")
    assert result.exit_code == 0

def test_financial_indicator():
    result = run_cmd(["financial", "indicator", "--ts-code", "000001.SZ"], module="financial")
    assert result.exit_code == 0

# Concepts
def test_concepts_board():
    result = run_cmd(["concepts", "board"], module="concepts")
    assert result.exit_code == 0

def test_concepts_members():
    result = run_cmd(["concepts", "members", "--ts-code", "BK0001"], module="concepts")
    assert result.exit_code == 0

def test_concepts_daily():
    result = run_cmd(["concepts", "daily", "--ts-code", "BK0001"], module="concepts")
    assert result.exit_code == 0

def test_concepts_moneyflow():
    result = run_cmd(["concepts", "moneyflow", "--ts-code", "BK0001"], module="concepts")
    assert result.exit_code == 0

def test_concepts_volume_anomaly():
    result = run_cmd(["concepts", "volume-anomaly"], module="concepts")
    assert result.exit_code == 0

def test_concepts_hot_boards():
    result = run_cmd(["concepts", "hot-boards"], module="concepts")
    assert result.exit_code == 0

def test_concepts_rank_alpha():
    result = run_cmd(["concepts", "rank-alpha"], module="concepts")
    assert result.exit_code == 0

def test_concepts_rank_alpha_velocity():
    result = run_cmd(["concepts", "rank-alpha-velocity"], module="concepts")
    assert result.exit_code == 0

# Alpha
def test_alpha_sector_strategy():
    result = run_cmd(["alpha", "sector-strategy", "--sector-code", "801010.SI"], module="alpha")
    assert result.exit_code == 0

def test_alpha_rank_l1():
    result = run_cmd(["alpha", "rank-l1"], module="alpha")
    assert result.exit_code == 0

def test_alpha_rank_l2():
    result = run_cmd(["alpha", "rank-l2"], module="alpha")
    assert result.exit_code == 0

def test_alpha_rank_l1_full():
    result = run_cmd(["alpha", "rank-l1-full"], module="alpha")
    assert result.exit_code == 0

def test_alpha_rank_l1_velocity():
    result = run_cmd(["alpha", "rank-l1-velocity"], module="alpha")
    assert result.exit_code == 0

def test_alpha_rank_l2_velocity():
    result = run_cmd(["alpha", "rank-l2-velocity"], module="alpha")
    assert result.exit_code == 0
