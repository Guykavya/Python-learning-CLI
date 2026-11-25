## Hint 1

How can you count the non-missing cells of every row at once (`notna()` gives True/False cells; what does summing along
`axis=1` give)? If you sort by two columns, which one decides first? After that sort, where in each key group is the
best row, and which `keep=` of `drop_duplicates` finds it? What must you do to keep ties in table order?

## Hint 2

```text
work = df with a fresh 0..n-1 index
work["_filled"] = work.notna().sum(axis=1)               # count BEFORE adding more columns, or subtract
order = work.sort_values(["_filled", "updated_at"], kind="stable")   # best row of a group is the last one
winners = order.drop_duplicates(subset=key, keep="last").index
return df[work.index.isin(winners)]
```
