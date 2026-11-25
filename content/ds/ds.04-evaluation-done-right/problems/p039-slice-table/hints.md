## Hint 1

How do you get, for each value of `col`, the **positions** of its rows? Look at `groupby(col).indices`.

## Hint 2

```text
for value, idx in frame.groupby(col).indices.items():
    auc = roc_auc_score(y[idx], p[idx]) if both classes in y[idx] else nan
    rows.append((value, len(idx), y[idx].mean(), p[idx].mean(), auc))
return DataFrame(rows, columns=[col, "rows", "base_rate", "mean_p", "auc"]).set_index(col).sort_index()
```
