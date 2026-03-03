# tushare_cli Design

**Date:** 2026-03-03
**Status:** Approved

## Summary

A standalone Python CLI query client in `tools/tushare_cli/` that wraps the Tushare `pro_api` directly, providing full parity with the 52 tools from [tushare_mcp](https://github.com/zhewenzhang/tushare_mcp). Built with Click command groups.

## Goals

- One-off data queries from the terminal
- Full parity with tushare_mcp's 52 financial data tools
- Configurable output: `table` (rich), `json`, `csv`
- Optional caching via `--cache` flag (off by default)
- Token from `--token` flag, `TUSHARE_TOKEN` env var, or `~/.tushare_cli/config.toml`

## Non-Goals

- Interactive REPL
- Batch processing / scripting engine
- MCP server integration
- Always-on caching

## Directory Structure

```
tools/tushare_cli/
├── __init__.py
├── main.py           # CLI entry point, root group with global options
├── config.py         # Token resolution (flag > env > config file)
├── output.py         # Formatters: table (rich), json, csv
├── cache.py          # File-based cache (used only when --cache is passed)
└── commands/
    ├── __init__.py
    ├── stock.py      # 22 stock market tools
    ├── index.py      # 4 index tools
    ├── futures.py    # 5 futures tools
    ├── forex.py      # 1 forex tool
    ├── financial.py  # 2 financial statement tools
    ├── concepts.py   # 8 concept board tools
    └── alpha.py      # 6 alpha strategy tools
```

## Global Flags

Inherited by every command via Click context:

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--format` | `table\|json\|csv` | `table` | Output format |
| `--cache` | flag | off | Enable file-based response caching |
| `--token` | text | — | Override Tushare token for this invocation |

## Token Resolution

1. `--token` CLI flag (highest priority)
2. `TUSHARE_TOKEN` environment variable
3. `~/.tushare_cli/config.toml` config file

Config file management via `tushare_cli config set-token <token>`.

## Command Structure

```bash
# Config
tushare_cli config set-token <token>

# Stock (22 tools)
tushare_cli stock daily --ts-code 000001.SZ --start 20240101 --end 20240201
tushare_cli stock weekly --ts-code 000001.SZ --start 20240101
tushare_cli stock basic --name 平安银行
tushare_cli stock realtime --ts-code "6*.SH"
tushare_cli stock minute --ts-code 000001.SZ --freq 15MIN
# ... and more

# Index (4 tools)
tushare_cli index daily --ts-code 000300.SH --start 20240101
tushare_cli index global

# Futures (5 tools)
tushare_cli futures contracts --exchange CFFEX
tushare_cli futures holdings --ts-code IF2403.CFX

# Forex (1 tool)
tushare_cli forex daily --symbol USDCNH

# Financial statements (2 tools)
tushare_cli financial income --ts-code 000001.SZ --period 20231231

# Concept boards (8 tools)
tushare_cli concepts boards
tushare_cli concepts members --ts-code BK0001

# Alpha strategies (6 tools)
tushare_cli alpha sector-strength --date 20240101
```

## Output Formats

- **table** (default): Rich-formatted ASCII table with column headers
- **json**: Raw JSON array, suitable for piping to `jq`
- **csv**: Comma-separated, suitable for redirecting to files

## Caching

When `--cache` is passed, responses are stored in `~/.tushare_cli/cache/` as JSON files keyed by a hash of the API call + parameters. Cache is never invalidated automatically — users clear it manually.

## Dependencies

- `click` — CLI framework
- `tushare` — Tushare Pro API client
- `rich` — Table formatting
- `tomllib` / `tomli` — Config file parsing
- `pandas` — Data handling (already a tushare dependency)

## Reference

- tushare_mcp: https://github.com/zhewenzhang/tushare_mcp
- Tushare Pro API docs: https://tushare.pro/document/2
