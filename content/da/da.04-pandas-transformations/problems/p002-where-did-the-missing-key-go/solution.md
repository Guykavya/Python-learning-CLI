## Approach

Mark the rows with a missing key first: rows 1 and 4 (sales 5 and 7). Everything else follows from "dropped unless
`dropna=False`".

1. `a` sums S1 (10 + 30 = 40), S2 (20) and S3 (1). The `None` rows are in no group: `{'S1': 40, 'S2': 20, 'S3': 1}`.
2. `a.sum()` is 61, but the table holds 73. The 12 missing are the two rows without a store.
3. With `dropna=False` a fourth group appears, **last** in the sorted result: `4 [40, 20, 1, 12]`. Now the totals
   reconcile (40 + 20 + 1 + 12 = 73).
4. `size()` counts rows per group: `[2, 1, 1]`; the missing-key rows are not in any group.
5. With `dropna=False`: `[2, 1, 1, 2]`.
6. `t["store"].count()` counts non-missing values in the column: 4 of the 6 rows.

## Output

```text
{'S1': 40, 'S2': 20, 'S3': 1}
61 73
4 [40, 20, 1, 12]
[2, 1, 1]
[2, 1, 1, 2]
4 6
```

## Another way

To check any grouped total in one line: `t.groupby("store", dropna=False)["sales"].sum().sum() == t["sales"].sum()`.
To see the lost rows: `t[t["store"].isna()]`.
