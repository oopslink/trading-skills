---
name: tushare-cli-patterns
description: >
  Patterns and conventions for extending tushare-cli — the Click-based CLI tool
  at tools/tushare_cli/ that wraps the Tushare Pro financial data API.
  Use this skill whenever the user asks to: add a new tushare command, add a new
  command group, fix a tushare CLI bug, write tests for CLI commands, or work with
  any file under tools/tushare_cli/ or tests/tushare_cli/. Also trigger when the
  user mentions tushare, tushare-cli, pro_api, or wants to query A-share / futures
  / forex / index data from the terminal.
source: local-git-analysis
analyzed_commits: 15
---

# tushare-cli Patterns

## Project Layout

```
tools/tushare_cli/
├── pyproject.toml              # entry point: tushare-cli = "tushare_cli.main:cli"
├── requirements.txt
├── README.md
└── src/tushare_cli/            # src/ layout — package root
    ├── api.py                  # SHARED: get_pro(), call_api(), safe_call()
    ├── config.py               # Token resolution + save_token()
    ├── cache.py                # File-based cache (~/.tushare_cli/cache/)
    ├── output.py               # format_output(df, fmt) → table/json/csv
    ├── main.py                 # CLI root group (--format / --cache / --token)
    └── commands/
        ├── stock.py            # 22 tools
        ├── index.py            # 4 tools
        ├── futures.py          # 5 tools
        ├── forex.py            # 1 tool
        ├── financial.py        # 2 tools
        ├── concepts.py         # 8 tools
        └── alpha.py            # 6 tools

tests/tushare_cli/              # Mirrors commands/ structure
├── test_config.py
├── test_cache.py
├── test_output.py
├── test_main.py
├── test_commands_stock.py
├── test_commands_index.py
├── test_commands_futures.py
└── test_commands_remaining.py  # forex + financial + concepts + alpha
```

## The Command Pattern

Every command follows this exact 4-line body:

```python
@group.command("kebab-name")
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def command_name(ctx, ts_code, trade_date, start_date, end_date):
    """One-line docstring."""
    pro = get_pro(ctx)
    params = {"ts_code": ts_code, "trade_date": trade_date,
              "start_date": start_date, "end_date": end_date}
    df = call_api(ctx, "api_name", params,
                  lambda: pro.tushare_method(**params))
    click.echo(format_output(df, ctx.obj["fmt"]))
```

Key rules:
- Always `@click.pass_context` — context carries `fmt`, `cache`, `token`
- Always use `call_api()` — never call `pro.*()` directly; this is what makes `--cache` work
- `api_name` should be unique per command (used as the cache key prefix), e.g. `"stock_daily"`, `"fut_holding"`
- `format_output(df, ctx.obj["fmt"])` handles all three output modes automatically
- Never import `resolve_token` in command files — it lives in `api.py`

## Shared API Module (`api.py`)

```python
from tushare_cli.api import get_pro, call_api
```

- `get_pro(ctx)` — resolves token, calls `ts.set_token()`, returns `ts.pro_api()`
- `call_api(ctx, api_name, params, api_func)` — checks cache first, calls API on miss, writes cache on hit, wraps errors via `safe_call()`
- `safe_call(func)` — converts tushare exceptions into `click.ClickException` with helpful messages

Never define a local `get_pro()` in a command file. Import from `api.py`.

## Adding a New Command to an Existing Group

1. Add the function to the appropriate `commands/<group>.py`
2. Add a test to the corresponding `tests/tushare_cli/test_commands_<group>.py`
3. Mock the new tushare method in the test's `MagicMock` setup

Example — adding `stock block-trade`:

```python
# commands/stock.py
@stock.command("block-trade")
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def block_trade(ctx, ts_code, trade_date, start_date, end_date):
    """Block trade records."""
    pro = get_pro(ctx)
    params = {"ts_code": ts_code, "trade_date": trade_date,
              "start_date": start_date, "end_date": end_date}
    df = call_api(ctx, "block_trade", params,
                  lambda: pro.block_trade(**params))
    click.echo(format_output(df, ctx.obj["fmt"]))
```

## Adding a New Command Group

1. Create `tools/tushare_cli/src/tushare_cli/commands/<group>.py`
2. Define `@click.group()` with the group name
3. Import from `tushare_cli.api` — never define local `get_pro()`
4. Register in `main.py`: `from tushare_cli.commands.<group> import <group>` + `cli.add_command(<group>)`
5. Create `tests/tushare_cli/test_commands_<group>.py` with `run_cmd()` helper

## Test Pattern

Every command test file follows this template:

```python
import pandas as pd
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from tushare_cli.main import cli

MOCK_DF = pd.DataFrame({"ts_code": ["000001.SZ"], "close": [10.5]})

def run_cmd(args):
    pro = MagicMock()
    for m in ["method_a", "method_b"]:          # list all tushare methods this group uses
        getattr(pro, m).return_value = MOCK_DF
    runner = CliRunner()
    with patch("tushare.pro_api", return_value=pro):
        with patch("tushare_cli.api.resolve_token", return_value="fake"):
            return runner.invoke(cli, args)

def test_command_name():
    result = run_cmd(["group", "subcommand", "--ts-code", "000001.SZ"])
    assert result.exit_code == 0
```

Important:
- Patch target for resolve_token is always `tushare_cli.api.resolve_token` (not the command module)
- Always patch `tushare.pro_api`, not `tushare_cli.commands.<group>.ts`
- Run tests with `python3.11 -m pytest tests/tushare_cli/ -v`

## Commit Conventions

All commits follow conventional commits:

| Prefix | Use for |
|--------|---------|
| `feat(tushare-cli):` | New commands or features |
| `fix(tushare-cli):` | Bug fixes |
| `docs(tushare-cli):` | README, docstrings, design docs |
| `test(tushare-cli):` | Test-only changes |
| `refactor(tushare-cli):` | Internal restructuring, no behavior change |

## Token & Config

- Token resolution order: `--token` flag → `TUSHARE_TOKEN` env var → `~/.tushare_cli/config.toml`
- Config file written with `chmod(0o600)` — never world-readable
- `tushare-cli config set-token <token>` persists to config file

## Output Formats

`--format` is a global option inherited by all commands:

```bash
tushare-cli --format table   # default, rich ASCII table
tushare-cli --format json    # JSON array (pipe to jq)
tushare-cli --format csv     # CSV (redirect to file)
```

Handled entirely by `format_output(df, fmt)` in `output.py` — no command needs to think about this.

## Caching

`--cache` is a global flag. When enabled, `call_api()` in `api.py`:
1. Checks `~/.tushare_cli/cache/<sha256_hash>.json` before calling the API
2. Returns cached DataFrame on hit (no network call)
3. Writes result on miss

Cache never expires automatically. Users clear with `rm ~/.tushare_cli/cache/*.json`.

## Running the CLI

```bash
# installed editable under Python 3.11
tushare-cli --help
tushare-cli stock daily --ts-code 000001.SZ --start 20240101
tushare-cli --format json index sw-daily --ts-code 801010.SI
tushare-cli --cache futures contracts --exchange CFFEX

# or via python module
python3.11 -c "from tushare_cli.main import cli; from click.testing import CliRunner; print(CliRunner().invoke(cli, ['stock', 'basic', '--ts-code', '000001.SZ']).output)"
```
