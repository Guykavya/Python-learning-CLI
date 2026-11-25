## Hint 1

Which rows must be next to each other before "the previous month" means anything? What does `pct_change` give for
`0 → 40` and for `0 → 0`? Which of those two needs fixing?

## Hint 2

```text
out = monthly.sort_values(["store_id", "month"], ignore_index=True)
g = out.groupby("store_id")["revenue"].pct_change() * 100
out["growth_pct"] = g.replace([inf, -inf], NaN)          # numpy: np.inf, np.nan
```
