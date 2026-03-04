---
name: tushare-alpha
description: Use when performing sector rotation analysis, ranking Shenwan industry sectors by return or momentum, or building a sector strategy screen using tushare-cli. Triggers on: 行业轮动, 板块排名, 行业强弱, 动量, sector rotation.
---

# tushare-alpha: Sector Rotation & Ranking

## Commands

```bash
tushare-cli alpha rank-l1          --end-date 20240201   # L1 sector ranking
tushare-cli alpha rank-l2          --end-date 20240201   # L2 sector ranking
tushare-cli alpha rank-l1-velocity --end-date 20240201   # L1 momentum / velocity
tushare-cli alpha rank-l2-velocity --end-date 20240201   # L2 momentum / velocity
tushare-cli alpha rank-l1-full     --end-date 20240201   # L1 full detail
tushare-cli alpha sector-strategy  --sector-code 801010.SI --end-date 20240201
```

## Common Workflows

### Top 5 sectors by today's return
```bash
tushare-cli --format json alpha rank-l1 --end-date 20240201 | \
  jq 'sort_by(-.pct_chg) | .[:5]'
```

### Momentum leaders (velocity ranking)
```bash
tushare-cli --format json alpha rank-l1-velocity --end-date 20240201 | \
  jq 'sort_by(-.velocity) | .[:5]'
```
