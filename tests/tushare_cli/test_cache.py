import pandas as pd
from unittest.mock import patch
from tushare_cli.cache import get_cached, set_cached, make_key


def test_make_key_deterministic():
    k1 = make_key("stock_daily", {"ts_code": "000001.SZ", "start_date": "20240101"})
    k2 = make_key("stock_daily", {"start_date": "20240101", "ts_code": "000001.SZ"})
    assert k1 == k2


def test_make_key_differs_by_api():
    k1 = make_key("stock_daily", {"ts_code": "000001.SZ"})
    k2 = make_key("stock_weekly", {"ts_code": "000001.SZ"})
    assert k1 != k2


def test_cache_roundtrip(tmp_path):
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    key = "testkey123"
    with patch("tushare_cli.cache.CACHE_DIR", tmp_path):
        set_cached(key, df)
        result = get_cached(key)
    assert result is not None
    assert list(result.columns) == ["a", "b"]
    assert result["a"].tolist() == [1, 2]


def test_cache_miss_returns_none(tmp_path):
    with patch("tushare_cli.cache.CACHE_DIR", tmp_path):
        result = get_cached("nonexistent_key")
    assert result is None
