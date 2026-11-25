## Approach

Summarise each store once (labels, sum, mean, size), then read every line off that summary.

| Store | Labels | Sum | Mean | Size |
|---|---|---|---|---|
| S1 | 0, 2, 5, 7 | 100 | 25 | 4 |
| S2 | 1, 4 | 90 | 45 | 2 |
| S3 | 3, 6 | 20 | 10 | 2 |

1. `agg("sum")`: one value per store, sorted: `3 [100, 90, 20]`.
2. `transform("sum")`: each of the 8 rows gets its store's total, in row order:
   `8 [100, 90, 100, 20, 90, 100, 20, 100]`.
3. `filter`: stores with a total of at least 90 are S1 and S2; their original rows, labels in order:
   `6 [0, 1, 2, 4, 5, 7]`.
4. The same idea as a mask: stores whose mean is above 15 are S1 (25) and S2 (45): `6 ['S1', 'S2']`.
5. `size()` per store `[4, 2, 2]`, and `head(1)` keeps one row per store: 3 rows.

## Output

```text
3 [100, 90, 20]
8 [100, 90, 100, 20, 90, 100, 20, 100]
6 [0, 1, 2, 4, 5, 7]
6 ['S1', 'S2']
[4, 2, 2] 3
```

## Another way

To check shapes in your own code, print `len(result)` and `result.index[:5].tolist()` after each step: one row per
group means `agg`, the input's labels mean `transform`, `filter` or a mask.
