import pandas as pd
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from tushare_cli.main import cli

MOCK_DF = pd.DataFrame({"ts_code": ["000001.SZ"], "close": [10.5]})


def make_pro_mock():
    pro = MagicMock()
    for method in ["stock_basic", "daily", "weekly", "fund_daily", "index_daily",
                   "stk_holdertrade", "stk_holdernumber", "moneyflow_dc", "stk_surv",
                   "cyq_perf", "daily_basic", "top_list", "top_inst", "rt_min",
                   "rt_min_daily", "rt_k", "share_float", "repurchase",
                   "pledge_detail", "block_trade"]:
        getattr(pro, method).return_value = MOCK_DF
    return pro


def run_cmd(args):
    runner = CliRunner()
    pro_mock = make_pro_mock()
    with patch("tushare.pro_api", return_value=pro_mock):
        with patch("tushare_cli.api.resolve_token", return_value="fake_token"):
            return runner.invoke(cli, args)


def test_stock_basic():
    result = run_cmd(["stock", "basic", "--ts-code", "000001.SZ"])
    assert result.exit_code == 0

def test_stock_search():
    result = run_cmd(["stock", "search", "--keyword", "平安"])
    assert result.exit_code == 0

def test_stock_daily():
    result = run_cmd(["stock", "daily", "--ts-code", "000001.SZ",
                      "--start", "20240101", "--end", "20240201"])
    assert result.exit_code == 0

def test_stock_weekly():
    result = run_cmd(["stock", "weekly", "--ts-code", "000001.SZ"])
    assert result.exit_code == 0

def test_stock_etf_daily():
    result = run_cmd(["stock", "etf-daily", "--ts-code", "510300.SH"])
    assert result.exit_code == 0

def test_stock_holder_trade():
    result = run_cmd(["stock", "holder-trade", "--ts-code", "000001.SZ"])
    assert result.exit_code == 0

def test_stock_holder_number():
    result = run_cmd(["stock", "holder-number", "--ts-code", "000001.SZ"])
    assert result.exit_code == 0

def test_stock_moneyflow():
    result = run_cmd(["stock", "moneyflow", "--ts-code", "000001.SZ"])
    assert result.exit_code == 0

def test_stock_survey():
    result = run_cmd(["stock", "survey", "--ts-code", "000001.SZ"])
    assert result.exit_code == 0

def test_stock_cyq_perf():
    result = run_cmd(["stock", "cyq-perf", "--ts-code", "000001.SZ"])
    assert result.exit_code == 0

def test_stock_daily_basic():
    result = run_cmd(["stock", "daily-basic", "--ts-code", "000001.SZ"])
    assert result.exit_code == 0

def test_stock_top_list():
    result = run_cmd(["stock", "top-list", "--trade-date", "20240101"])
    assert result.exit_code == 0

def test_stock_top_inst():
    result = run_cmd(["stock", "top-inst", "--trade-date", "20240101"])
    assert result.exit_code == 0

def test_stock_minute():
    result = run_cmd(["stock", "minute", "--ts-code", "000001.SZ"])
    assert result.exit_code == 0

def test_stock_rt_k():
    result = run_cmd(["stock", "rt-k", "--ts-code", "000001.SZ"])
    assert result.exit_code == 0

def test_stock_share_float():
    result = run_cmd(["stock", "share-float", "--ts-code", "000001.SZ"])
    assert result.exit_code == 0

def test_stock_repurchase():
    result = run_cmd(["stock", "repurchase"])
    assert result.exit_code == 0

def test_stock_pledge_detail():
    result = run_cmd(["stock", "pledge-detail", "--ts-code", "000001.SZ"])
    assert result.exit_code == 0

def test_stock_block_trade():
    result = run_cmd(["stock", "block-trade", "--ts-code", "000001.SZ"])
    assert result.exit_code == 0

def test_stock_index_daily():
    result = run_cmd(["stock", "index-daily", "--ts-code", "000300.SH"])
    assert result.exit_code == 0

def test_stock_sector_strength():
    result = run_cmd(["stock", "sector-strength"])
    assert result.exit_code == 0

def test_stock_sector_health():
    result = run_cmd(["stock", "sector-health"])
    assert result.exit_code == 0

def test_stock_list_default():
    result = run_cmd(["stock", "list"])
    assert result.exit_code == 0

def test_stock_list_with_exchange():
    result = run_cmd(["stock", "list", "--exchange", "SSE"])
    assert result.exit_code == 0

def test_stock_list_with_list_status():
    result = run_cmd(["stock", "list", "--list-status", "D"])
    assert result.exit_code == 0

def test_stock_json_format():
    result = run_cmd(["--format", "json", "stock", "daily", "--ts-code", "000001.SZ"])
    assert result.exit_code == 0
    assert "ts_code" in result.output


def test_cache_prevents_second_api_call(tmp_path, monkeypatch):
    """Cache hit should prevent second API call."""
    monkeypatch.setattr("tushare_cli.cache.CACHE_DIR", tmp_path)
    pro_mock = make_pro_mock()
    runner = CliRunner()
    with patch("tushare.pro_api", return_value=pro_mock):
        with patch("tushare_cli.api.resolve_token", return_value="fake"):
            # First call — should hit API and write cache
            result1 = runner.invoke(cli, ["--cache", "stock", "daily",
                                          "--ts-code", "000001.SZ"])
            assert result1.exit_code == 0
            assert pro_mock.daily.call_count == 1

            # Second call — should hit cache, NOT call API again
            result2 = runner.invoke(cli, ["--cache", "stock", "daily",
                                          "--ts-code", "000001.SZ"])
            assert result2.exit_code == 0
            assert pro_mock.daily.call_count == 1  # still 1, not 2
