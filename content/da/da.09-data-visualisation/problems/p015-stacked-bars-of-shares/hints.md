## Hint 1

You need a table with one row per group and one column per part. Which pandas call builds it from the long format? Which operation turns counts into percentages of the row total?

## Hint 2

```text
groups = df[group].unique(); parts = df[part].unique()
tbl = df.groupby([group, part])[value].sum().unstack(fill_value=0).reindex(index=groups, columns=parts, fill_value=0)
pct = tbl.div(tbl.sum(axis=1), axis=0) * 100
bottom = zeros
for p in parts: ax.bar(groups, pct[p], bottom=bottom, label=p); bottom += pct[p]
```
