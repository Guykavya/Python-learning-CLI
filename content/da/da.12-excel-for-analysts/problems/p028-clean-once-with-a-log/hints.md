## Hint 1

Clean a copy first, keep the original next to it, and compare column by column to build the log. Decide which rows are bad **after** cleaning (a repaired code is fine). Remember to leave the quarantined rows as they were.

## Hint 2

```text
c = df.copy(); c["region"] = ...; c["units"] = pd.to_numeric(..., errors="coerce"); c["product_code"] = ...
bad = ~c.region.isin(regions) | c.units.isna() | ~c.product_code.isin(valid_codes)
for i in c.index[~bad]: for field in (region, units, product_code): if df.at[i, f] != c.at[i, f] (watch the types): log
```
