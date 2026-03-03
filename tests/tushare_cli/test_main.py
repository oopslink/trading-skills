from click.testing import CliRunner
from tushare_cli.main import cli


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output


def test_config_set_token(tmp_path):
    from unittest.mock import patch
    import tushare_cli.config as cfg
    runner = CliRunner()
    with patch.object(cfg, "CONFIG_PATH", tmp_path / "config.toml"):
        result = runner.invoke(cli, ["config", "set-token", "mytoken123"])
    assert result.exit_code == 0
    assert "saved" in result.output.lower()


def test_stock_group_exists():
    runner = CliRunner()
    result = runner.invoke(cli, ["stock", "--help"])
    assert result.exit_code == 0


def test_index_group_exists():
    runner = CliRunner()
    result = runner.invoke(cli, ["index", "--help"])
    assert result.exit_code == 0


def test_format_option_accepted():
    runner = CliRunner()
    result = runner.invoke(cli, ["--format", "json", "--help"])
    assert result.exit_code == 0


def test_invalid_format_rejected():
    runner = CliRunner()
    result = runner.invoke(cli, ["--format", "xml"])
    assert result.exit_code != 0
