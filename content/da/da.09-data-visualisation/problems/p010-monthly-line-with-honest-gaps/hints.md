## Hint 1

After grouping by month, which months are missing from the index? Which pandas method adds the missing index values, and what does it fill them with by default?

## Hint 2

```text
m = df.groupby(month start)["revenue"].sum()
full = pd.date_range(m.index.min(), m.index.max(), freq="MS")
m = m.reindex(full)                      # missing months become NaN
ax.plot(m.index, m.values)
```
