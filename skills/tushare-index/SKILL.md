---
name: tushare-index
description: Use when querying Shenwan industry index (申万) daily data, sector constituents, or global market indices (S&P 500, Nikkei, HSI) using tushare-cli. Triggers on: 申万, 行业指数, 成分股, 全球指数.
---

# tushare-index: Shenwan & Global Index Queries

## Commands

```bash
# Shenwan index daily data
tushare-cli index sw-daily --ts-code 801010.SI --start 20240101 --end 20240201

# List Shenwan codes by level
tushare-cli index classify           # all L1 codes
tushare-cli index classify --level 2 # L2 codes

# Constituent stocks of a Shenwan index
tushare-cli index sw-members --ts-code 801010.SI

# Global indices
tushare-cli index global
```

## Key Shenwan L1 Codes

| Code | Sector | Code | Sector |
|------|--------|------|--------|
| 801010.SI | Agriculture | 801080.SI | Electronics |
| 801020.SI | Mining | 801110.SI | Home Appliances |
| 801030.SI | Chemicals | 801140.SI | Retail |
| 801040.SI | Steel | 801160.SI | Public Utilities |
| 801170.SI | Transportation | 801180.SI | Real Estate |
| 801200.SI | Finance | 801210.SI | Banks |
| 801230.SI | Non-ferrous | 801750.SI | Computers |
| 801760.SI | Media | 801770.SI | Telecom |
| 801780.SI | Financials | 801790.SI | Non-bank Finance |
| 801880.SI | Autos | 801890.SI | Machinery |

## Common Workflow

### All stocks in a sector
```bash
tushare-cli index sw-members --ts-code 801080.SI   # Electronics constituents
```
