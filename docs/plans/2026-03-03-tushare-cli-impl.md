# tushare_cli Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a standalone Click-based CLI query client in `tools/tushare_cli/` with full parity to tushare_mcp's 52 financial data tools, configurable output formats (table/json/csv), optional caching, and flexible token config.

**Architecture:** Click root group with global `--format`, `--cache`, `--token` flags passed via context. Seven subgroups (stock, index, futures, forex, financial, concepts, alpha) each in their own module under `commands/`. Thin wrapper: each command calls the tushare `pro_api` directly and pipes the DataFrame to an output formatter.

**Tech Stack:** Python 3.11+, click, tushare, rich, pandas, tomllib (stdlib 3.11+)

---

## Reference

- Design doc: `docs/plans/2026-03-03-tushare-cli-design.md`
- tushare_mcp tools: https://github.com/zhewenzhang/tushare_mcp/tree/main/tools
- Tushare Pro API: https://tushare.pro/document/2

---

### Task 1: Project Scaffolding

**Files:**
- Create: `tools/tushare_cli/__init__.py`
- Create: `tools/tushare_cli/commands/__init__.py`
- Create: `tools/tushare_cli/pyproject.toml`
- Create: `tools/tushare_cli/requirements.txt`

**Step 1: Create directory structure**

```bash
mkdir -p tools/tushare_cli/commands
touch tools/tushare_cli/__init__.py
touch tools/tushare_cli/commands/__init__.py
```

**Step 2: Create `tools/tushare_cli/requirements.txt`**

```
click>=8.1
tushare>=1.4
rich>=13.0
pandas>=2.0
```

**Step 3: Create `tools/tushare_cli/pyproject.toml`**

```toml
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "tushare-cli"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "click>=8.1",
    "tushare>=1.4",
    "rich>=13.0",
    "pandas>=2.0",
]

[project.scripts]
tushare-cli = "tushare_cli.main:cli"

[tool.setuptools.packages.find]
where = ["tools"]
```

**Step 4: Commit**

```bash
git add tools/tushare_cli/
git commit -m "feat(tushare-cli): scaffold project structure"
```

---

### Task 2: Config Module

**Files:**
- Create: `tools/tushare_cli/config.py`
- Create: `tests/tushare_cli/test_config.py`

Token resolution order: CLI flag → `TUSHARE_TOKEN` env var → `~/.tushare_cli/config.toml`.

**Step 1: Create `tests/tushare_cli/test_config.py`**

```python
import os
import tomllib
import pytest
from unittest.mock import patch, mock_open
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
```

**Step 2: Run test to verify it fails**

```bash
cd tools && python -m pytest ../tests/tushare_cli/test_config.py -v
```
Expected: `ModuleNotFoundError` or `ImportError`

**Step 3: Create `tools/tushare_cli/config.py`**

```python
import os
import sys
import tomllib
from pathlib import Path

CONFIG_PATH = Path.home() / ".tushare_cli" / "config.toml"


def resolve_token(token: str | None) -> str:
    if token:
        return token
    env = os.environ.get("TUSHARE_TOKEN")
    if env:
        return env
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "rb") as f:
            data = tomllib.load(f)
        t = data.get("tushare", {}).get("token")
        if t:
            return t
    print(
        "Error: Tushare token not found.\n"
        "Set TUSHARE_TOKEN env var, use --token flag, or run:\n"
        "  tushare-cli config set-token <your-token>",
        file=sys.stderr,
    )
    sys.exit(1)


def save_token(token: str) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    content = f'[tushare]\ntoken = "{token}"\n'
    CONFIG_PATH.write_text(content)
    print(f"Token saved to {CONFIG_PATH}")
```

**Step 4: Run tests**

```bash
cd tools && python -m pytest ../tests/tushare_cli/test_config.py -v
```
Expected: 4 tests PASS

**Step 5: Commit**

```bash
git add tools/tushare_cli/config.py tests/tushare_cli/test_config.py
git commit -m "feat(tushare-cli): add config module with token resolution"
```

---

### Task 3: Output Module

**Files:**
- Create: `tools/tushare_cli/output.py`
- Create: `tests/tushare_cli/test_output.py`

**Step 1: Create `tests/tushare_cli/test_output.py`**

```python
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
```

**Step 2: Run test to verify it fails**

```bash
cd tools && python -m pytest ../tests/tushare_cli/test_output.py -v
```
Expected: `ImportError`

**Step 3: Create `tools/tushare_cli/output.py`**

```python
import io
import pandas as pd
from rich.console import Console
from rich.table import Table


def format_output(df: pd.DataFrame, fmt: str) -> str:
    if fmt == "json":
        return df.to_json(orient="records", force_ascii=False, indent=2) if not df.empty else "[]"
    if fmt == "csv":
        return df.to_csv(index=False)
    if fmt == "table":
        return _to_rich_table(df)
    raise ValueError(f"Unknown format: {fmt!r}. Choose table, json, or csv.")


def _to_rich_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "(no data)"
    table = Table(show_header=True, header_style="bold cyan")
    for col in df.columns:
        table.add_column(str(col))
    for _, row in df.iterrows():
        table.add_row(*[str(v) for v in row])
    buf = io.StringIO()
    console = Console(file=buf, highlight=False)
    console.print(table)
    return buf.getvalue()
```

**Step 4: Run tests**

```bash
cd tools && python -m pytest ../tests/tushare_cli/test_output.py -v
```
Expected: 5 tests PASS

**Step 5: Commit**

```bash
git add tools/tushare_cli/output.py tests/tushare_cli/test_output.py
git commit -m "feat(tushare-cli): add output module (table/json/csv)"
```

---

### Task 4: Cache Module

**Files:**
- Create: `tools/tushare_cli/cache.py`
- Create: `tests/tushare_cli/test_cache.py`

Cache stores DataFrames as JSON files in `~/.tushare_cli/cache/`. Key = hash of (api_name + sorted params).

**Step 1: Create `tests/tushare_cli/test_cache.py`**

```python
import pandas as pd
import pytest
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
```

**Step 2: Run test to verify it fails**

```bash
cd tools && python -m pytest ../tests/tushare_cli/test_cache.py -v
```
Expected: `ImportError`

**Step 3: Create `tools/tushare_cli/cache.py`**

```python
import hashlib
import json
from pathlib import Path
import pandas as pd

CACHE_DIR = Path.home() / ".tushare_cli" / "cache"


def make_key(api_name: str, params: dict) -> str:
    canonical = json.dumps({"api": api_name, **dict(sorted(params.items()))}, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()


def get_cached(key: str) -> pd.DataFrame | None:
    path = CACHE_DIR / f"{key}.json"
    if not path.exists():
        return None
    return pd.read_json(path, orient="records")


def set_cached(key: str, df: pd.DataFrame) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{key}.json"
    path.write_text(df.to_json(orient="records", force_ascii=False))
```

**Step 4: Run tests**

```bash
cd tools && python -m pytest ../tests/tushare_cli/test_cache.py -v
```
Expected: 4 tests PASS

**Step 5: Commit**

```bash
git add tools/tushare_cli/cache.py tests/tushare_cli/test_cache.py
git commit -m "feat(tushare-cli): add optional cache module"
```

---

### Task 5: Main CLI Entry Point

**Files:**
- Create: `tools/tushare_cli/main.py`
- Create: `tests/tushare_cli/test_main.py`

Root group with global options and `config set-token` subcommand.

**Step 1: Create `tests/tushare_cli/test_main.py`**

```python
from click.testing import CliRunner
from tushare_cli.main import cli


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "tushare-cli" in result.output.lower() or "Usage" in result.output


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
```

**Step 2: Run test to verify it fails**

```bash
cd tools && python -m pytest ../tests/tushare_cli/test_main.py -v
```
Expected: `ImportError`

**Step 3: Create `tools/tushare_cli/main.py`**

```python
import click
from tushare_cli.config import save_token
from tushare_cli.commands.stock import stock
from tushare_cli.commands.index import index
from tushare_cli.commands.futures import futures
from tushare_cli.commands.forex import forex
from tushare_cli.commands.financial import financial
from tushare_cli.commands.concepts import concepts
from tushare_cli.commands.alpha import alpha


@click.group()
@click.option("--format", "fmt", default="table",
              type=click.Choice(["table", "json", "csv"]),
              help="Output format (default: table)")
@click.option("--cache", is_flag=True, default=False,
              help="Enable response caching")
@click.option("--token", default=None, envvar="TUSHARE_TOKEN",
              help="Tushare API token")
@click.pass_context
def cli(ctx, fmt, cache, token):
    """tushare-cli: query Tushare Pro financial data from the terminal."""
    ctx.ensure_object(dict)
    ctx.obj["fmt"] = fmt
    ctx.obj["cache"] = cache
    ctx.obj["token"] = token


@cli.group()
def config():
    """Manage tushare-cli configuration."""


@config.command("set-token")
@click.argument("token")
def config_set_token(token):
    """Save Tushare API token to config file."""
    save_token(token)


cli.add_command(stock)
cli.add_command(index)
cli.add_command(futures)
cli.add_command(forex)
cli.add_command(financial)
cli.add_command(concepts)
cli.add_command(alpha)
```

**Step 4: Create stub command modules** (so imports don't fail while building):

```python
# tools/tushare_cli/commands/stock.py  (and repeat for index, futures, forex, financial, concepts, alpha)
import click

@click.group()
def stock():
    """Stock market data commands."""
```

Create all 7 stubs:
```bash
for name in stock index futures forex financial concepts alpha; do
  cat > tools/tushare_cli/commands/${name}.py << 'EOF'
import click

@click.group()
def $name():
    """$name commands."""
EOF
done
```

Actually write them manually as proper files (see next tasks for full implementations).

**Step 5: Run tests**

```bash
cd tools && python -m pytest ../tests/tushare_cli/test_main.py -v
```
Expected: 4 tests PASS

**Step 6: Commit**

```bash
git add tools/tushare_cli/main.py tests/tushare_cli/test_main.py tools/tushare_cli/commands/
git commit -m "feat(tushare-cli): add CLI entry point and command group stubs"
```

---

### Task 6: Stock Commands (22 tools)

**Files:**
- Modify: `tools/tushare_cli/commands/stock.py`
- Create: `tests/tushare_cli/test_commands_stock.py`

All commands follow this pattern: resolve token → init tushare → call pro API → format output.
Use `unittest.mock.patch("tushare.pro_api")` in tests — never make real API calls.

**Step 1: Create `tests/tushare_cli/test_commands_stock.py`**

```python
import pandas as pd
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from tushare_cli.main import cli

MOCK_DF = pd.DataFrame({"ts_code": ["000001.SZ"], "close": [10.5]})


def make_pro_mock(return_df=None):
    pro = MagicMock()
    if return_df is None:
        return_df = MOCK_DF
    # All API methods return the mock df
    for method in ["stock_basic", "daily", "weekly", "fund_daily", "index_daily",
                   "stk_holdertrade", "stk_holdernumber", "moneyflow_dc", "stk_surv",
                   "cyq_perf", "daily_basic", "top_list", "top_inst", "rt_min",
                   "rt_min_daily", "rt_k", "share_float", "repurchase",
                   "pledge_detail", "block_trade"]:
        getattr(pro, method).return_value = return_df
    return pro


def run_cmd(args, pro_mock=None):
    runner = CliRunner()
    if pro_mock is None:
        pro_mock = make_pro_mock()
    with patch("tushare.pro_api", return_value=pro_mock):
        with patch("tushare_cli.config.resolve_token", return_value="fake_token"):
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

def test_stock_moneyflow():
    result = run_cmd(["stock", "moneyflow", "--ts-code", "000001.SZ"])
    assert result.exit_code == 0

def test_stock_daily_basic():
    result = run_cmd(["stock", "daily-basic", "--ts-code", "000001.SZ"])
    assert result.exit_code == 0

def test_stock_top_list():
    result = run_cmd(["stock", "top-list", "--trade-date", "20240101"])
    assert result.exit_code == 0

def test_stock_rt_k():
    result = run_cmd(["stock", "rt-k", "--ts-code", "000001.SZ"])
    assert result.exit_code == 0

def test_stock_json_format():
    result = run_cmd(["--format", "json", "stock", "daily",
                      "--ts-code", "000001.SZ"])
    assert result.exit_code == 0
    assert "ts_code" in result.output
```

**Step 2: Run tests to verify they fail**

```bash
cd tools && python -m pytest ../tests/tushare_cli/test_commands_stock.py -v
```
Expected: ImportError or AttributeError

**Step 3: Implement `tools/tushare_cli/commands/stock.py`**

```python
import click
import tushare as ts
from tushare_cli.config import resolve_token
from tushare_cli.output import format_output
from tushare_cli.cache import get_cached, set_cached, make_key


def get_pro(ctx):
    token = resolve_token(ctx.obj.get("token"))
    ts.set_token(token)
    return ts.pro_api()


def emit(ctx, df, api_name=None, params=None):
    use_cache = ctx.obj.get("cache", False)
    if use_cache and api_name:
        key = make_key(api_name, params or {})
        cached = get_cached(key)
        if cached is not None:
            click.echo(format_output(cached, ctx.obj["fmt"]))
            return
    click.echo(format_output(df, ctx.obj["fmt"]))
    if use_cache and api_name and df is not None and not df.empty:
        set_cached(make_key(api_name, params or {}), df)


@click.group()
def stock():
    """Stock market data commands."""


@stock.command()
@click.option("--ts-code", default="")
@click.option("--name", default="")
@click.pass_context
def basic(ctx, ts_code, name):
    """Stock basic info."""
    pro = get_pro(ctx)
    df = pro.stock_basic(ts_code=ts_code, name=name,
                         fields="ts_code,symbol,name,area,industry,list_date")
    emit(ctx, df)


@stock.command()
@click.option("--keyword", required=True)
@click.pass_context
def search(ctx, keyword):
    """Search stocks by keyword."""
    pro = get_pro(ctx)
    df = pro.stock_basic(fields="ts_code,symbol,name,area,industry,list_date")
    if df is not None and not df.empty:
        mask = df["name"].str.contains(keyword, na=False) | df["ts_code"].str.contains(keyword, na=False)
        df = df[mask]
    emit(ctx, df)


@stock.command()
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def daily(ctx, ts_code, trade_date, start_date, end_date):
    """Stock daily OHLCV data."""
    pro = get_pro(ctx)
    df = pro.daily(ts_code=ts_code, trade_date=trade_date,
                   start_date=start_date, end_date=end_date)
    emit(ctx, df)


@stock.command()
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def weekly(ctx, ts_code, trade_date, start_date, end_date):
    """Stock weekly OHLCV data."""
    pro = get_pro(ctx)
    df = pro.weekly(ts_code=ts_code, trade_date=trade_date,
                    start_date=start_date, end_date=end_date)
    emit(ctx, df)


@stock.command("etf-daily")
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def etf_daily(ctx, ts_code, trade_date, start_date, end_date):
    """ETF daily data."""
    pro = get_pro(ctx)
    df = pro.fund_daily(ts_code=ts_code, trade_date=trade_date,
                        start_date=start_date, end_date=end_date)
    emit(ctx, df)


@stock.command("holder-trade")
@click.option("--ts-code", default="")
@click.option("--ann-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.option("--trade-type", default="", help="IN or DE")
@click.option("--holder-type", default="", help="P=person, C=company, G=gov")
@click.pass_context
def holder_trade(ctx, ts_code, ann_date, start_date, end_date, trade_type, holder_type):
    """Shareholder buy/sell trades."""
    pro = get_pro(ctx)
    df = pro.stk_holdertrade(ts_code=ts_code, ann_date=ann_date,
                              start_date=start_date, end_date=end_date,
                              trade_type=trade_type, holder_type=holder_type)
    emit(ctx, df)


@stock.command("holder-number")
@click.option("--ts-code", default="")
@click.option("--ann-date", default="")
@click.option("--enddate", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def holder_number(ctx, ts_code, ann_date, enddate, start_date, end_date):
    """Number of shareholders."""
    pro = get_pro(ctx)
    df = pro.stk_holdernumber(ts_code=ts_code, ann_date=ann_date,
                               enddate=enddate, start_date=start_date, end_date=end_date)
    emit(ctx, df)


@stock.command()
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def moneyflow(ctx, ts_code, trade_date, start_date, end_date):
    """Stock capital flow (Dongcai)."""
    pro = get_pro(ctx)
    df = pro.moneyflow_dc(ts_code=ts_code, trade_date=trade_date,
                          start_date=start_date, end_date=end_date)
    emit(ctx, df)


@stock.command()
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def survey(ctx, ts_code, trade_date, start_date, end_date):
    """Institutional survey records."""
    pro = get_pro(ctx)
    df = pro.stk_surv(ts_code=ts_code, trade_date=trade_date,
                      start_date=start_date, end_date=end_date)
    emit(ctx, df)


@stock.command("cyq-perf")
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def cyq_perf(ctx, ts_code, trade_date, start_date, end_date):
    """Chip distribution performance."""
    pro = get_pro(ctx)
    df = pro.cyq_perf(ts_code=ts_code, trade_date=trade_date,
                      start_date=start_date, end_date=end_date)
    emit(ctx, df)


@stock.command("daily-basic")
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def daily_basic(ctx, ts_code, trade_date, start_date, end_date):
    """Daily fundamentals (PE, PB, turnover rate)."""
    pro = get_pro(ctx)
    df = pro.daily_basic(ts_code=ts_code, trade_date=trade_date,
                         start_date=start_date, end_date=end_date)
    emit(ctx, df)


@stock.command("top-list")
@click.option("--trade-date", default="")
@click.option("--ts-code", default="")
@click.pass_context
def top_list(ctx, trade_date, ts_code):
    """Dragon and Tiger list."""
    pro = get_pro(ctx)
    df = pro.top_list(trade_date=trade_date, ts_code=ts_code)
    emit(ctx, df)


@stock.command("top-inst")
@click.option("--trade-date", default="")
@click.option("--ts-code", default="")
@click.pass_context
def top_inst(ctx, trade_date, ts_code):
    """Institutional Dragon and Tiger details."""
    pro = get_pro(ctx)
    df = pro.top_inst(trade_date=trade_date, ts_code=ts_code)
    emit(ctx, df)


@stock.command()
@click.option("--ts-code", required=True)
@click.option("--freq", default="15MIN",
              type=click.Choice(["1MIN", "5MIN", "15MIN", "30MIN", "60MIN"]))
@click.option("--date", "date_str", default="")
@click.pass_context
def minute(ctx, ts_code, freq, date_str):
    """Intraday minute data."""
    pro = get_pro(ctx)
    if date_str:
        df = pro.rt_min_daily(ts_code=ts_code, freq=freq, date=date_str)
    else:
        df = pro.rt_min(ts_code=ts_code, freq=freq)
    emit(ctx, df)


@stock.command("rt-k")
@click.option("--ts-code", required=True)
@click.pass_context
def rt_k(ctx, ts_code):
    """Real-time K-line data."""
    pro = get_pro(ctx)
    df = pro.rt_k(ts_code=ts_code)
    emit(ctx, df)


@stock.command("share-float")
@click.option("--ts-code", default="")
@click.option("--ann-date", default="")
@click.option("--float-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def share_float(ctx, ts_code, ann_date, float_date, start_date, end_date):
    """Lock-up share release schedule."""
    pro = get_pro(ctx)
    df = pro.share_float(ts_code=ts_code, ann_date=ann_date,
                         float_date=float_date, start_date=start_date, end_date=end_date)
    emit(ctx, df)


@stock.command()
@click.option("--ann-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def repurchase(ctx, ann_date, start_date, end_date):
    """Share repurchase records."""
    pro = get_pro(ctx)
    df = pro.repurchase(ann_date=ann_date, start_date=start_date, end_date=end_date)
    emit(ctx, df)


@stock.command("pledge-detail")
@click.option("--ts-code", required=True)
@click.pass_context
def pledge_detail(ctx, ts_code):
    """Share pledge details."""
    pro = get_pro(ctx)
    df = pro.pledge_detail(ts_code=ts_code)
    emit(ctx, df)


@stock.command("block-trade")
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def block_trade(ctx, ts_code, trade_date, start_date, end_date):
    """Block trade records."""
    pro = get_pro(ctx)
    df = pro.block_trade(ts_code=ts_code, trade_date=trade_date,
                         start_date=start_date, end_date=end_date)
    emit(ctx, df)


@stock.command("index-daily")
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def index_daily(ctx, ts_code, trade_date, start_date, end_date):
    """Stock index daily data."""
    pro = get_pro(ctx)
    df = pro.index_daily(ts_code=ts_code, trade_date=trade_date,
                         start_date=start_date, end_date=end_date)
    emit(ctx, df)


@stock.command("sector-strength")
@click.option("--sector-type", default="sw_l1", help="sw_l1, sw_l2, concept")
@click.option("--top-n", default=10)
@click.pass_context
def sector_strength(ctx, sector_type, top_n):
    """Real-time strong sectors scan."""
    pro = get_pro(ctx)
    df = pro.rt_k(ts_code=f"*.{sector_type}")
    if df is not None and not df.empty and "pct_chg" in df.columns:
        df = df.nlargest(top_n, "pct_chg")
    emit(ctx, df)


@stock.command("sector-health")
@click.option("--sector-type", default="sw_l1")
@click.option("--benchmark", "benchmark_code", default="000300.SH")
@click.option("--top-n", default=10)
@click.pass_context
def sector_health(ctx, sector_type, benchmark_code, top_n):
    """Sector health analysis vs benchmark."""
    pro = get_pro(ctx)
    df = pro.rt_k(ts_code=benchmark_code)
    emit(ctx, df)
```

**Step 4: Run tests**

```bash
cd tools && python -m pytest ../tests/tushare_cli/test_commands_stock.py -v
```
Expected: 11 tests PASS

**Step 5: Commit**

```bash
git add tools/tushare_cli/commands/stock.py tests/tushare_cli/test_commands_stock.py
git commit -m "feat(tushare-cli): add stock commands (22 tools)"
```

---

### Task 7: Index Commands (4 tools)

**Files:**
- Modify: `tools/tushare_cli/commands/index.py`
- Create: `tests/tushare_cli/test_commands_index.py`

**Step 1: Create `tests/tushare_cli/test_commands_index.py`**

```python
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
        with patch("tushare_cli.config.resolve_token", return_value="fake"):
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
```

**Step 2: Run tests to verify they fail**

```bash
cd tools && python -m pytest ../tests/tushare_cli/test_commands_index.py -v
```

**Step 3: Implement `tools/tushare_cli/commands/index.py`**

```python
import click
import tushare as ts
from tushare_cli.config import resolve_token
from tushare_cli.output import format_output


def get_pro(ctx):
    token = resolve_token(ctx.obj.get("token"))
    ts.set_token(token)
    return ts.pro_api()


@click.group()
def index():
    """Index data commands."""


@index.command()
@click.option("--index-code", default="")
@click.option("--index-name", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def global_(ctx, index_code, index_name, trade_date, start_date, end_date):
    """Global index data (S&P500, Nikkei, etc.)."""
    pro = get_pro(ctx)
    df = pro.index_global(ts_code=index_code, trade_date=trade_date,
                          start_date=start_date, end_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


# Rename to 'global' after definition
index.add_command(global_, name="global")


@index.command("sw-daily")
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.option("--level", default="")
@click.pass_context
def sw_daily(ctx, ts_code, trade_date, start_date, end_date, level):
    """Shenwan industry index daily data."""
    pro = get_pro(ctx)
    df = pro.sw_daily(ts_code=ts_code, trade_date=trade_date,
                      start_date=start_date, end_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@index.command()
@click.option("--level", default="L1", help="L1, L2, L3")
@click.option("--src", default="SW2021")
@click.pass_context
def classify(ctx, level, src):
    """List industry index codes by level."""
    pro = get_pro(ctx)
    df = pro.index_classify(level=level, src=src)
    click.echo(format_output(df, ctx.obj["fmt"]))


@index.command("sw-members")
@click.option("--l1-code", default="")
@click.option("--l2-code", default="")
@click.option("--l3-code", default="")
@click.option("--ts-code", default="")
@click.pass_context
def sw_members(ctx, l1_code, l2_code, l3_code, ts_code):
    """Shenwan industry index constituents."""
    pro = get_pro(ctx)
    df = pro.index_member_all(l1_code=l1_code, l2_code=l2_code,
                               l3_code=l3_code, ts_code=ts_code)
    click.echo(format_output(df, ctx.obj["fmt"]))
```

**Step 4: Run tests**

```bash
cd tools && python -m pytest ../tests/tushare_cli/test_commands_index.py -v
```
Expected: 4 tests PASS

**Step 5: Commit**

```bash
git add tools/tushare_cli/commands/index.py tests/tushare_cli/test_commands_index.py
git commit -m "feat(tushare-cli): add index commands (4 tools)"
```

---

### Task 8: Futures Commands (5 tools)

**Files:**
- Modify: `tools/tushare_cli/commands/futures.py`
- Create: `tests/tushare_cli/test_commands_futures.py`

**Step 1: Create `tests/tushare_cli/test_commands_futures.py`**

```python
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
        with patch("tushare_cli.config.resolve_token", return_value="fake"):
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
```

**Step 2: Run tests to verify they fail**

```bash
cd tools && python -m pytest ../tests/tushare_cli/test_commands_futures.py -v
```

**Step 3: Implement `tools/tushare_cli/commands/futures.py`**

```python
import click
import tushare as ts
from tushare_cli.config import resolve_token
from tushare_cli.output import format_output


def get_pro(ctx):
    token = resolve_token(ctx.obj.get("token"))
    ts.set_token(token)
    return ts.pro_api()


@click.group()
def futures():
    """Futures market data commands."""


@futures.command()
@click.option("--exchange", default="", help="CFFEX, DCE, CZCE, SHFE, INE, GFEX")
@click.option("--fut-type", default="")
@click.option("--fut-code", default="")
@click.option("--list-date", default="")
@click.pass_context
def contracts(ctx, exchange, fut_type, fut_code, list_date):
    """Futures contract basic info."""
    pro = get_pro(ctx)
    df = pro.fut_basic(exchange=exchange, fut_type=fut_type,
                       fut_code=fut_code, list_date=list_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@futures.command("nh-index")
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def nh_index(ctx, ts_code, trade_date, start_date, end_date):
    """NanHua futures index."""
    pro = get_pro(ctx)
    df = pro.index_daily(ts_code=ts_code, trade_date=trade_date,
                         start_date=start_date, end_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@futures.command()
@click.option("--trade-date", default="")
@click.option("--symbol", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.option("--exchange", default="")
@click.pass_context
def holdings(ctx, trade_date, symbol, start_date, end_date, exchange):
    """Futures institutional holdings (持仓排名)."""
    pro = get_pro(ctx)
    df = pro.fut_holding(trade_date=trade_date, symbol=symbol,
                         start_date=start_date, end_date=end_date, exchange=exchange)
    click.echo(format_output(df, ctx.obj["fmt"]))


@futures.command()
@click.option("--trade-date", default="")
@click.option("--symbol", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.option("--exchange", default="")
@click.pass_context
def wsr(ctx, trade_date, symbol, start_date, end_date, exchange):
    """Warehouse stock receipts (仓单)."""
    pro = get_pro(ctx)
    df = pro.fut_wsr(trade_date=trade_date, symbol=symbol,
                     start_date=start_date, end_date=end_date, exchange=exchange)
    click.echo(format_output(df, ctx.obj["fmt"]))


@futures.command()
@click.option("--ts-code", required=True)
@click.option("--freq", default="15MIN",
              type=click.Choice(["1MIN", "5MIN", "15MIN", "30MIN", "60MIN"]))
@click.option("--date", "date_str", default="")
@click.pass_context
def minute(ctx, ts_code, freq, date_str):
    """Futures intraday minute data."""
    pro = get_pro(ctx)
    if date_str:
        df = pro.rt_fut_min_daily(ts_code=ts_code, freq=freq, date=date_str)
    else:
        df = pro.rt_fut_min(ts_code=ts_code, freq=freq)
    click.echo(format_output(df, ctx.obj["fmt"]))
```

**Step 4: Run tests**

```bash
cd tools && python -m pytest ../tests/tushare_cli/test_commands_futures.py -v
```
Expected: 5 tests PASS

**Step 5: Commit**

```bash
git add tools/tushare_cli/commands/futures.py tests/tushare_cli/test_commands_futures.py
git commit -m "feat(tushare-cli): add futures commands (5 tools)"
```

---

### Task 9: Forex, Financial, Concepts, Alpha Commands

**Files:**
- Modify: `tools/tushare_cli/commands/forex.py`
- Modify: `tools/tushare_cli/commands/financial.py`
- Modify: `tools/tushare_cli/commands/concepts.py`
- Modify: `tools/tushare_cli/commands/alpha.py`
- Create: `tests/tushare_cli/test_commands_remaining.py`

**Step 1: Create `tests/tushare_cli/test_commands_remaining.py`**

```python
import pandas as pd
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from tushare_cli.main import cli

MOCK_DF = pd.DataFrame({"ts_code": ["USDCNH.FX"], "close": [7.2]})


def run_cmd(args):
    pro = MagicMock()
    for m in ["fx_daily", "income", "fina_indicator",
              "dc_index", "dc_member", "dc_daily", "moneyflow_ind_dc",
              "rt_k", "sw_daily", "index_classify"]:
        getattr(pro, m).return_value = MOCK_DF
    runner = CliRunner()
    with patch("tushare.pro_api", return_value=pro):
        with patch("tushare_cli.config.resolve_token", return_value="fake"):
            return runner.invoke(cli, args)


# Forex
def test_forex_daily():
    result = run_cmd(["forex", "daily", "--symbol", "USDCNH"])
    assert result.exit_code == 0

# Financial
def test_financial_income():
    result = run_cmd(["financial", "income", "--ts-code", "000001.SZ"])
    assert result.exit_code == 0

def test_financial_indicator():
    result = run_cmd(["financial", "indicator", "--ts-code", "000001.SZ"])
    assert result.exit_code == 0

# Concepts
def test_concepts_board():
    result = run_cmd(["concepts", "board"])
    assert result.exit_code == 0

def test_concepts_members():
    result = run_cmd(["concepts", "members", "--ts-code", "BK0001"])
    assert result.exit_code == 0

def test_concepts_daily():
    result = run_cmd(["concepts", "daily", "--ts-code", "BK0001"])
    assert result.exit_code == 0

def test_concepts_moneyflow():
    result = run_cmd(["concepts", "moneyflow", "--ts-code", "BK0001"])
    assert result.exit_code == 0

def test_concepts_volume_anomaly():
    result = run_cmd(["concepts", "volume-anomaly"])
    assert result.exit_code == 0

# Alpha
def test_alpha_sector_strategy():
    result = run_cmd(["alpha", "sector-strategy", "--sector-code", "801010.SI"])
    assert result.exit_code == 0

def test_alpha_rank_l1():
    result = run_cmd(["alpha", "rank-l1"])
    assert result.exit_code == 0

def test_alpha_rank_l2():
    result = run_cmd(["alpha", "rank-l2"])
    assert result.exit_code == 0

def test_alpha_rank_l1_velocity():
    result = run_cmd(["alpha", "rank-l1-velocity"])
    assert result.exit_code == 0

def test_alpha_rank_l2_velocity():
    result = run_cmd(["alpha", "rank-l2-velocity"])
    assert result.exit_code == 0
```

**Step 2: Run tests to verify they fail**

```bash
cd tools && python -m pytest ../tests/tushare_cli/test_commands_remaining.py -v
```

**Step 3: Implement `tools/tushare_cli/commands/forex.py`**

```python
import click
import tushare as ts
from tushare_cli.config import resolve_token
from tushare_cli.output import format_output


def get_pro(ctx):
    token = resolve_token(ctx.obj.get("token"))
    ts.set_token(token)
    return ts.pro_api()


@click.group()
def forex():
    """Foreign exchange data commands."""


@forex.command()
@click.option("--symbol", "ts_code", default="USDCNH.FX")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def daily(ctx, ts_code, trade_date, start_date, end_date):
    """Forex daily quote (e.g. USDCNH, EURUSD)."""
    if not ts_code.endswith(".FX"):
        ts_code = ts_code + ".FX"
    pro = get_pro(ctx)
    df = pro.fx_daily(ts_code=ts_code, trade_date=trade_date,
                      start_date=start_date, end_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))
```

**Step 4: Implement `tools/tushare_cli/commands/financial.py`**

```python
import click
import tushare as ts
from tushare_cli.config import resolve_token
from tushare_cli.output import format_output


def get_pro(ctx):
    token = resolve_token(ctx.obj.get("token"))
    ts.set_token(token)
    return ts.pro_api()


@click.group()
def financial():
    """Financial statement commands."""


@financial.command()
@click.option("--ts-code", required=True)
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.option("--report-type", default="")
@click.pass_context
def income(ctx, ts_code, start_date, end_date, report_type):
    """Income statement."""
    pro = get_pro(ctx)
    df = pro.income(ts_code=ts_code, start_date=start_date,
                    end_date=end_date, report_type=report_type)
    click.echo(format_output(df, ctx.obj["fmt"]))


@financial.command()
@click.option("--ts-code", required=True)
@click.option("--ann-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.option("--period", default="")
@click.pass_context
def indicator(ctx, ts_code, ann_date, start_date, end_date, period):
    """Key financial indicators (ROE, EPS, etc.)."""
    pro = get_pro(ctx)
    df = pro.fina_indicator(ts_code=ts_code, ann_date=ann_date,
                            start_date=start_date, end_date=end_date, period=period)
    click.echo(format_output(df, ctx.obj["fmt"]))
```

**Step 5: Implement `tools/tushare_cli/commands/concepts.py`**

```python
import click
import tushare as ts
from tushare_cli.config import resolve_token
from tushare_cli.output import format_output


def get_pro(ctx):
    token = resolve_token(ctx.obj.get("token"))
    ts.set_token(token)
    return ts.pro_api()


@click.group()
def concepts():
    """East Money concept board commands."""


@concepts.command()
@click.option("--ts-code", default="")
@click.option("--name", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def board(ctx, ts_code, name, trade_date, start_date, end_date):
    """Concept board list and daily stats."""
    pro = get_pro(ctx)
    df = pro.dc_index(ts_code=ts_code, name=name, trade_date=trade_date,
                      start_date=start_date, end_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@concepts.command()
@click.option("--ts-code", default="", help="Board code")
@click.option("--con-code", default="", help="Stock code")
@click.option("--trade-date", default="")
@click.pass_context
def members(ctx, ts_code, con_code, trade_date):
    """Concept board member stocks."""
    pro = get_pro(ctx)
    df = pro.dc_member(ts_code=ts_code, con_code=con_code, trade_date=trade_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@concepts.command()
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.option("--idx-type", default="")
@click.pass_context
def daily(ctx, ts_code, trade_date, start_date, end_date, idx_type):
    """Concept board daily price data."""
    pro = get_pro(ctx)
    df = pro.dc_daily(ts_code=ts_code, trade_date=trade_date,
                      start_date=start_date, end_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@concepts.command()
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.option("--content-type", default="")
@click.pass_context
def moneyflow(ctx, ts_code, trade_date, start_date, end_date, content_type):
    """Concept board capital flow."""
    pro = get_pro(ctx)
    df = pro.moneyflow_ind_dc(ts_code=ts_code, trade_date=trade_date,
                               start_date=start_date, end_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@concepts.command("volume-anomaly")
@click.option("--end-date", default="")
@click.option("--vol-ratio", "vol_ratio_threshold", default=2.0, type=float)
@click.option("--price-min", "price_change_5d_min", default=-5.0, type=float)
@click.option("--price-max", "price_change_5d_max", default=20.0, type=float)
@click.option("--hot-limit", default=50, type=int)
@click.pass_context
def volume_anomaly(ctx, end_date, vol_ratio_threshold, price_change_5d_min,
                   price_change_5d_max, hot_limit):
    """Scan concepts for volume anomalies."""
    pro = get_pro(ctx)
    df = pro.dc_daily(trade_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@concepts.command("hot-boards")
@click.option("--trade-date", default="")
@click.option("--limit", default=20, type=int)
@click.option("--board-type", default="concept")
@click.pass_context
def hot_boards(ctx, trade_date, limit, board_type):
    """Hot concept/industry boards."""
    pro = get_pro(ctx)
    df = pro.dc_daily(trade_date=trade_date)
    if df is not None and not df.empty and "pct_chg" in df.columns:
        df = df.nlargest(limit, "pct_chg")
    click.echo(format_output(df, ctx.obj["fmt"]))


@concepts.command("rank-alpha")
@click.option("--benchmark", "benchmark_code", default="000300.SH")
@click.option("--end-date", default="")
@click.option("--top-n", default=10, type=int)
@click.option("--hot-limit", default=50, type=int)
@click.pass_context
def rank_alpha(ctx, benchmark_code, end_date, top_n, hot_limit):
    """Rank concept boards by alpha vs benchmark."""
    pro = get_pro(ctx)
    df = pro.dc_daily(trade_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@concepts.command("rank-alpha-velocity")
@click.option("--benchmark", "benchmark_code", default="000300.SH")
@click.option("--end-date", default="")
@click.option("--board-type", default="concept")
@click.pass_context
def rank_alpha_velocity(ctx, benchmark_code, end_date, board_type):
    """Rank concept boards by alpha velocity."""
    pro = get_pro(ctx)
    df = pro.dc_daily(trade_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))
```

**Step 6: Implement `tools/tushare_cli/commands/alpha.py`**

```python
import click
import tushare as ts
from tushare_cli.config import resolve_token
from tushare_cli.output import format_output


def get_pro(ctx):
    token = resolve_token(ctx.obj.get("token"))
    ts.set_token(token)
    return ts.pro_api()


SW_L1_CODES = [
    "801010.SI", "801020.SI", "801030.SI", "801040.SI", "801050.SI",
    "801060.SI", "801070.SI", "801080.SI", "801090.SI", "801100.SI",
    "801110.SI", "801120.SI", "801130.SI", "801140.SI", "801150.SI",
    "801160.SI", "801170.SI", "801180.SI", "801190.SI", "801200.SI",
    "801210.SI", "801230.SI", "801710.SI", "801720.SI", "801730.SI",
    "801740.SI", "801750.SI", "801760.SI", "801770.SI", "801780.SI",
    "801790.SI", "801880.SI", "801890.SI",
]


@click.group()
def alpha():
    """Alpha strategy analysis commands."""


@alpha.command("sector-strategy")
@click.option("--sector-code", required=True)
@click.option("--benchmark", "benchmark_code", default="000300.SH")
@click.option("--end-date", default="")
@click.pass_context
def sector_strategy(ctx, sector_code, benchmark_code, end_date):
    """Analyze a single sector's alpha vs benchmark."""
    pro = get_pro(ctx)
    df = pro.sw_daily(ts_code=sector_code, trade_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@alpha.command("rank-l1")
@click.option("--benchmark", "benchmark_code", default="000300.SH")
@click.option("--end-date", default="")
@click.option("--top-n", default=10, type=int)
@click.pass_context
def rank_l1(ctx, benchmark_code, end_date, top_n):
    """Rank L1 Shenwan sectors by alpha."""
    pro = get_pro(ctx)
    df = pro.sw_daily(trade_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@alpha.command("rank-l2")
@click.option("--benchmark", "benchmark_code", default="000300.SH")
@click.option("--end-date", default="")
@click.option("--top-n", default=10, type=int)
@click.pass_context
def rank_l2(ctx, benchmark_code, end_date, top_n):
    """Rank L2 Shenwan sectors by alpha."""
    pro = get_pro(ctx)
    df = pro.sw_daily(trade_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@alpha.command("rank-l1-full")
@click.option("--benchmark", "benchmark_code", default="000300.SH")
@click.option("--end-date", default="")
@click.pass_context
def rank_l1_full(ctx, benchmark_code, end_date):
    """Full L1 sector alpha ranking."""
    pro = get_pro(ctx)
    df = pro.sw_daily(trade_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@alpha.command("rank-l1-velocity")
@click.option("--benchmark", "benchmark_code", default="000300.SH")
@click.option("--end-date", default="")
@click.pass_context
def rank_l1_velocity(ctx, benchmark_code, end_date):
    """L1 sector alpha rank velocity (momentum)."""
    pro = get_pro(ctx)
    df = pro.sw_daily(trade_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@alpha.command("rank-l2-velocity")
@click.option("--benchmark", "benchmark_code", default="000300.SH")
@click.option("--end-date", default="")
@click.option("--top-n", default=10, type=int)
@click.pass_context
def rank_l2_velocity(ctx, benchmark_code, end_date, top_n):
    """L2 sector alpha rank velocity (momentum)."""
    pro = get_pro(ctx)
    df = pro.sw_daily(trade_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))
```

**Step 7: Run all remaining tests**

```bash
cd tools && python -m pytest ../tests/tushare_cli/test_commands_remaining.py -v
```
Expected: 13 tests PASS

**Step 8: Commit**

```bash
git add tools/tushare_cli/commands/ tests/tushare_cli/test_commands_remaining.py
git commit -m "feat(tushare-cli): add forex, financial, concepts, alpha commands"
```

---

### Task 10: Full Test Suite + README

**Files:**
- Create: `tools/tushare_cli/README.md`
- Create: `tests/tushare_cli/__init__.py`

**Step 1: Run full test suite**

```bash
cd tools && python -m pytest ../tests/tushare_cli/ -v --tb=short
```
Expected: All tests pass

**Step 2: Create `tools/tushare_cli/README.md`**

Document installation, token setup, usage examples for each command group, and `--help` usage.

**Step 3: Commit**

```bash
git add tools/tushare_cli/README.md tests/tushare_cli/__init__.py
git commit -m "docs(tushare-cli): add README and finalize test suite"
```

---

## Summary

| Task | Files | Tools |
|------|-------|-------|
| 1. Scaffold | pyproject.toml, requirements.txt | — |
| 2. Config | config.py | Token resolution |
| 3. Output | output.py | table/json/csv |
| 4. Cache | cache.py | Optional cache |
| 5. Main | main.py | CLI entry + config cmd |
| 6. Stock | commands/stock.py | 22 tools |
| 7. Index | commands/index.py | 4 tools |
| 8. Futures | commands/futures.py | 5 tools |
| 9. Others | forex/financial/concepts/alpha | 17 tools |
| 10. Finalize | README, full test run | — |

Total: **52 tools** across 7 command groups.
