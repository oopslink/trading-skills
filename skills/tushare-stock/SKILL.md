---
name: tushare-stock
description: Use when querying A-share individual stock data including price history, real-time quotes, capital flow, shareholders, block trades, pledges, ETF, or sector health using tushare-cli. Triggers on: 个股, 行情, 资金流向, 龙虎榜, 股东, 质押, ETF.
---

# tushare-stock: Individual Stock Queries

## Commands

```bash
# Lookup
tushare-cli stock list                                 # all listed A-shares
tushare-cli stock list --exchange SSE                  # Shanghai only (SSE/SZSE/BSE)
tushare-cli stock list --list-status D                 # delisted stocks (L/D/P)
tushare-cli stock basic  --ts-code 000001.SZ          # stock info
tushare-cli stock search --keyword 平安银行             # find code by name

# Price history
tushare-cli stock daily  --ts-code 000001.SZ --start 20240101 --end 20240201
tushare-cli stock weekly --ts-code 000001.SZ --start 20240101

# Fundamentals (PE, PB, turnover)
tushare-cli stock daily-basic --ts-code 000001.SZ --trade-date 20240201

# Real-time / intraday
tushare-cli stock rt-k   --ts-code 000001.SZ           # real-time K-line
tushare-cli stock minute --ts-code 000001.SZ            # intraday minute bars

# Capital flow
tushare-cli stock moneyflow --ts-code 000001.SZ --trade-date 20240201

# Dragon & Tiger / institutional
tushare-cli stock top-list   --trade-date 20240201      # Dragon & Tiger list
tushare-cli stock top-inst   --trade-date 20240201      # institutional detail
tushare-cli stock holder-trade  --ts-code 000001.SZ     # insider trades
tushare-cli stock holder-number --ts-code 000001.SZ     # shareholder count

# Block trades & pledges
tushare-cli stock block-trade   --ts-code 000001.SZ
tushare-cli stock pledge-detail --ts-code 000001.SZ

# ETF
tushare-cli stock etf-daily --ts-code 159915.SZ --start 20240101

# Sector benchmark
tushare-cli stock sector-health   --ts-code 801010.SI --start 20240101
tushare-cli stock sector-strength                       # real-time strong sectors
```

## Common Workflows

### Find code by name
```bash
tushare-cli stock search --keyword 宁德时代
# → returns ts_code like 300750.SZ
```

### Price comparison to CSV
```bash
tushare-cli --format csv stock daily --ts-code 000001.SZ --start 20240101 > ping_an.csv
tushare-cli --format csv stock daily --ts-code 600036.SH --start 20240101 > merchants.csv
```

### Capital flow for a stock
```bash
tushare-cli stock moneyflow --ts-code 300750.SZ --trade-date 20240201
```
