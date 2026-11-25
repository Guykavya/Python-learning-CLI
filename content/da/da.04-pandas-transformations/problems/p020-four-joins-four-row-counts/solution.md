## Approach

Count matches per key, then add the unmatched rows each join keeps.

| Key | in `cust` | in `orde` | Rows when matched | Kept by |
|---|---|---|---|---|
| C1 | 1 | 2 | 2 | all four joins |
| C3 | 1 | 1 | 1 | all four joins |
| C2, C4, C5 | 1 | 0 | 1 each (missing order) | left, outer |
| C9 | 0 | 1 | 1 (missing city) | right, outer |

- `inner`: 2 + 1 = 3 rows, in left key order: `['C1', 'C1', 'C3']`.
- `left`: 3 + 3 = 6 rows, every customer, C1 twice.
- `right`: 3 + 1 = 4 rows, in the order of `orde`: `['C1', 'C3', 'C1', 'C9']`.
- `outer`: 3 + 3 + 1 = 7 rows, keys sorted.
- `indicator=True` on the outer join: 3 `both`, 3 `left_only` (C2, C4, C5), 1 `right_only` (C9).
- In the left join, 3 rows have no order, so `order_id` holds `NaN` and becomes `float64`.
- The left join's `amount` adds to 50 + 20 + 70 = 140 (missing values skipped). The orders table holds 150: the 10 of
  the orphan order C9 is not in a left join that starts from customers.

## Output

```text
inner 3 ['C1', 'C1', 'C3']
left 6 ['C1', 'C1', 'C2', 'C3', 'C4', 'C5']
right 4 ['C1', 'C3', 'C1', 'C9']
outer 7 ['C1', 'C1', 'C2', 'C3', 'C4', 'C5', 'C9']
3 3 1
3 float64
140 150
```

## Another way

The outer join with `indicator=True` alone answers all four counts: `inner` = both, `left` = both + left_only,
`right` = both + right_only, `outer` = all three.
