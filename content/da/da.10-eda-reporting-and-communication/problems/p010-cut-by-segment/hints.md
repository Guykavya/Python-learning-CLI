## Hint 1

Select the rows of each period with `o["month"].between(pd.Period(start), pd.Period(end))`. For each period, what do `value_counts(normalize=True)` and `groupby(dim)["churned"].mean()` give you?

## Hint 2

```text
for name, (start, end) in (("before", before), ("after", after)):
    rows = o[month between start and end]
    share[name] = rows[dim].value_counts(normalize=True) * 100
    churn[name] = rows.groupby(dim)["churned"].mean() * 100
t = DataFrame of the four columns; dropna(); change = after - before; sort descending
```
