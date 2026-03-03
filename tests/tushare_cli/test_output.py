import json
import pandas as pd
from io import StringIO
from tushare_cli.output import format_output


SAMPLE_DF = pd.DataFrame({"ts_code": ["000001.SZ"], "close": [10.5], "vol": [100000]})


def test_format_json():
    out = format_output(SAMPLE_DF, fmt="json")
    data = json.loads(out)
    assert data[0]["ts_code"] == "000001.SZ"
    assert data[0]["close"] == 10.5


def test_format_csv():
    out = format_output(SAMPLE_DF, fmt="csv")
    reader = pd.read_csv(StringIO(out))
    assert reader["ts_code"].iloc[0] == "000001.SZ"


def test_format_table_returns_string():
    out = format_output(SAMPLE_DF, fmt="table")
    assert "ts_code" in out
    assert "000001.SZ" in out


def test_format_empty_df():
    empty = pd.DataFrame()
    out = format_output(empty, fmt="json")
    assert out == "[]"


def test_invalid_format_raises():
    import pytest
    with pytest.raises(ValueError, match="Unknown format"):
        format_output(SAMPLE_DF, fmt="xml")
