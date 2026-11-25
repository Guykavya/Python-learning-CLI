## Hint 1

For one `k`, which cohorts count? What do you divide by: the sum of **all** cohort sizes or only of the cohorts that reached `k`?

## Hint 2

```text
for k in ks:
    if k not in active.columns: NaN
    col = active[k]; ok = col.notna()
    value = col[ok].sum() / sizes[ok].sum()   (NaN if no ok)
```
