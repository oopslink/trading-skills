---
name: tushare-financial
description: Use when fetching A-share company financial statements including income statement or balance sheet using tushare-cli. Triggers on: 财务报表, 利润表, 资产负债表, financial statements.
---

# tushare-financial: Financial Statement Queries

## Commands

```bash
tushare-cli financial income  --ts-code 000001.SZ --period 20231231
tushare-cli financial balance --ts-code 000001.SZ --period 20231231
```

- `--period`: reporting period end date in `YYYYMMDD` (e.g., `20231231` for annual, `20230930` for Q3)
