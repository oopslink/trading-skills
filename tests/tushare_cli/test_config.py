import pytest
from unittest.mock import patch
from tushare_cli.config import resolve_token, save_token, CONFIG_PATH


def test_resolve_token_from_explicit():
    assert resolve_token(token="abc123") == "abc123"


def test_resolve_token_from_env(monkeypatch):
    monkeypatch.setenv("TUSHARE_TOKEN", "envtoken")
    assert resolve_token(token=None) == "envtoken"


def test_resolve_token_from_config(tmp_path, monkeypatch):
    monkeypatch.delenv("TUSHARE_TOKEN", raising=False)
    config_file = tmp_path / "config.toml"
    config_file.write_text('[tushare]\ntoken = "filetoken"\n')
    with patch("tushare_cli.config.CONFIG_PATH", config_file):
        assert resolve_token(token=None) == "filetoken"


def test_resolve_token_missing(monkeypatch, tmp_path):
    monkeypatch.delenv("TUSHARE_TOKEN", raising=False)
    with patch("tushare_cli.config.CONFIG_PATH", tmp_path / "nonexistent.toml"):
        with pytest.raises(SystemExit):
            resolve_token(token=None)
