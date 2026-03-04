---
name: tushare-forex
description: Use when querying forex currency pair daily exchange rate data using tushare-cli. Triggers on: 外汇, 汇率, forex, currency, USDCNH, EURUSD.
---

# tushare-forex: Forex Rate Queries

## Commands

```bash
tushare-cli forex daily --symbol USDCNH --start 20240101
tushare-cli forex daily --symbol EURUSD --start 20240101
```

- `--symbol`: currency pair code (e.g., `USDCNH`, `EURUSD`, `USDJPY`)
- `--start` / `--end`: date range in `YYYYMMDD`
