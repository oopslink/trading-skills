# tushare-cli

A command-line query client for [Tushare Pro](https://tushare.pro) financial data. Full parity with 52 data tools across 7 categories.

## Installation

```bash
pip install -e tools/tushare_cli/
```

## Token Setup

Choose one method (priority: --token > env var > config file):

```bash
# Option 1: config file (recommended, persists across sessions)
tushare-cli config set-token YOUR_TOKEN

# Option 2: environment variable
export TUSHARE_TOKEN=YOUR_TOKEN

# Option 3: per-command flag
tushare-cli --token YOUR_TOKEN stock daily --ts-code 000001.SZ
```

Get your token at https://tushare.pro/user/token

## Output Formats

```bash
tushare-cli --format table   # default, rich ASCII table
tushare-cli --format json    # JSON array, pipe to jq
tushare-cli --format csv     # CSV, redirect to file
```

## Caching

```bash
tushare-cli --cache stock daily --ts-code 000001.SZ  # saves to ~/.tushare_cli/cache/
```

## Commands

### Stock (22 tools)

```bash
tushare-cli stock basic --ts-code 000001.SZ
tushare-cli stock search --keyword 平安
tushare-cli stock daily --ts-code 000001.SZ --start 20240101 --end 20240201
tushare-cli stock weekly --ts-code 000001.SZ --start 20240101
tushare-cli stock etf-daily --ts-code 510300.SH
tushare-cli stock holder-trade --ts-code 000001.SZ --trade-type IN
tushare-cli stock holder-number --ts-code 000001.SZ
tushare-cli stock moneyflow --ts-code 000001.SZ --trade-date 20240101
tushare-cli stock survey --ts-code 000001.SZ
tushare-cli stock cyq-perf --ts-code 000001.SZ
tushare-cli stock daily-basic --ts-code 000001.SZ --trade-date 20240101
tushare-cli stock top-list --trade-date 20240101
tushare-cli stock top-inst --trade-date 20240101
tushare-cli stock minute --ts-code 000001.SZ --freq 15MIN
tushare-cli stock rt-k --ts-code 000001.SZ
tushare-cli stock share-float --ts-code 000001.SZ
tushare-cli stock repurchase --start 20240101
tushare-cli stock pledge-detail --ts-code 000001.SZ
tushare-cli stock block-trade --ts-code 000001.SZ
tushare-cli stock index-daily --ts-code 000300.SH --start 20240101
tushare-cli stock sector-strength --sector-type sw_l1 --top-n 10
tushare-cli stock sector-health --benchmark 000300.SH
```

### Index (4 tools)

```bash
tushare-cli index global --index-code SPX
tushare-cli index sw-daily --ts-code 801010.SI --start 20240101
tushare-cli index classify --level L1
tushare-cli index sw-members --l1-code 801010.SI
```

### Futures (5 tools)

```bash
tushare-cli futures contracts --exchange CFFEX
tushare-cli futures nh-index --ts-code NH0100.NH
tushare-cli futures holdings --trade-date 20240101 --exchange CFFEX
tushare-cli futures wsr --trade-date 20240101
tushare-cli futures minute --ts-code IF2403.CFX --freq 15MIN
```

### Forex (1 tool)

```bash
tushare-cli forex daily --symbol USDCNH
tushare-cli forex daily --symbol EURUSD --start 20240101 --end 20240201
```

### Financial Statements (2 tools)

```bash
tushare-cli financial income --ts-code 000001.SZ --start 20230101
tushare-cli financial indicator --ts-code 000001.SZ --period 20231231
```

### Concept Boards (8 tools)

```bash
tushare-cli concepts board --trade-date 20240101
tushare-cli concepts members --ts-code BK0001
tushare-cli concepts daily --ts-code BK0001 --start 20240101
tushare-cli concepts moneyflow --ts-code BK0001
tushare-cli concepts volume-anomaly --end-date 20240101 --vol-ratio 2.5
tushare-cli concepts hot-boards --limit 20
tushare-cli concepts rank-alpha --benchmark 000300.SH --top-n 10
tushare-cli concepts rank-alpha-velocity --benchmark 000300.SH
```

### Alpha Strategy (6 tools)

```bash
tushare-cli alpha sector-strategy --sector-code 801010.SI --benchmark 000300.SH
tushare-cli alpha rank-l1 --benchmark 000300.SH --top-n 10
tushare-cli alpha rank-l2 --benchmark 000300.SH --top-n 10
tushare-cli alpha rank-l1-full --benchmark 000300.SH
tushare-cli alpha rank-l1-velocity --benchmark 000300.SH
tushare-cli alpha rank-l2-velocity --benchmark 000300.SH --top-n 10
```

## Global Options

| Option | Default | Description |
|--------|---------|-------------|
| `--format` | `table` | Output format: `table`, `json`, `csv` |
| `--cache` | off | Cache responses in `~/.tushare_cli/cache/` |
| `--token` | — | Override token for this invocation |

Use `--help` at any level for full option details:
```bash
tushare-cli --help
tushare-cli stock --help
tushare-cli stock daily --help
```
