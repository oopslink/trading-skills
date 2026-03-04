---
name: tushare-futures
description: Use when querying futures contracts, institutional futures holdings, futures intraday bars, NanHua commodity indices, or warehouse receipts using tushare-cli. Triggers on: 期货, 持仓, 仓单, futures.
---

# tushare-futures: Futures Queries

## Commands

```bash
# All contracts for an exchange
tushare-cli futures contracts --exchange CFFEX    # CFFEX / DCE / SHFE / CZCE

# Institutional holdings for a contract
tushare-cli futures holdings --ts-code IF2403.CFX

# Intraday minute bars
tushare-cli futures minute --ts-code IF2403.CFX

# NanHua commodity index
tushare-cli futures nh-index --ts-code NH0100.NHF

# Warehouse receipts
tushare-cli futures wsr --trade-date 20240201
```

## Common Workflow

### Top holders for a contract
```bash
tushare-cli --format json futures holdings --ts-code IF2406.CFX | \
  jq 'sort_by(-.vol) | .[:5]'
```
