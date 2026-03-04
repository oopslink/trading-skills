---
name: tushare-concepts
description: Use when querying concept boards (概念板块), hot concept boards, board capital flow, board constituent stocks, or scanning for volume anomalies across boards using tushare-cli. Triggers on: 概念板块, 热点板块, 涨幅榜, 量能异动.
---

# tushare-concepts: Concept Board Queries

## Commands

```bash
# Today's hot boards ranked by price change
tushare-cli concepts hot-boards --trade-date 20240201

# All boards with daily stats
tushare-cli concepts board --trade-date 20240201

# Stocks in a board
tushare-cli concepts members --ts-code BK0714       # e.g., AI concept

# Capital flow into boards
tushare-cli concepts moneyflow --trade-date 20240201

# Volume anomaly scanner
tushare-cli concepts volume-anomaly --end-date 20240201 --vol-ratio 2.0
```

## Common Workflows

### Top 10 hot boards today
```bash
tushare-cli concepts hot-boards --trade-date 20240201 --limit 10
```

### Boards attracting most capital
```bash
tushare-cli --format json concepts moneyflow --trade-date 20240201 | \
  jq 'sort_by(-.net_amount) | .[:10][] | {name, net_amount, pct_chg}'
```

### Potential breakout scan (vol > 3x, small price gain)
```bash
tushare-cli concepts volume-anomaly --end-date 20240201 --vol-ratio 3.0 --price-min 0 --price-max 10
```
