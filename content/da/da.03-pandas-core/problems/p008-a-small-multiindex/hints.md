## Hint 1

After `set_index(["region", "month"])`, what does `.loc[("N", "Feb"), "sales"]` return for a pair that does not exist? How can you turn that failure into 0? For the totals: what does `.loc["N", "sales"]` give (one region, all its months), and how do you get the list of regions from the index?

## Hint 2

```text
multi = df.set_index(["region", "month"])
sales_for:  try: int(multi.loc[(region, month), "sales"])   except KeyError: 0
regions = sorted(multi.index.get_level_values("region").unique())
sales_by_region: {r: int(multi.loc[r, "sales"].sum()) for r in regions}
```
