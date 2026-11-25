## Approach

Rank each store on its own, highest revenue first, then list the ranks in row order (labels 0 to 6).

| Label | Store | Revenue | dense | min | first | average |
|---|---|---|---|---|---|---|
| 0 | S1 | 50 | 2 | 3 | 3 | 3 |
| 1 | S1 | 80 | 1 | 1 | 1 | 1.5 |
| 2 | S2 | 30 | 2 | 2 | 2 | 2.5 |
| 3 | S1 | 80 | 1 | 1 | 2 | 1.5 |
| 4 | S2 | 90 | 1 | 1 | 1 | 1 |
| 5 | S2 | 30 | 2 | 2 | 3 | 2.5 |
| 6 | S1 | 20 | 3 | 4 | 4 | 4 |

`rank` returns floats, so lines 1, 2 and 4 print `2.0`; line 3 converts to `int` first. The last line lists the labels
whose dense rank is 1: the two 80s of S1 and the 90 of S2.

## Output

```text
[2.0, 1.0, 2.0, 1.0, 1.0, 2.0, 3.0]
[3.0, 1.0, 2.0, 1.0, 1.0, 2.0, 4.0]
[3, 1, 2, 2, 1, 3, 4]
[3.0, 1.5, 2.5, 1.5, 1.0, 2.5, 4.0]
[1, 3, 4]
```

## Another way

Check a rank column by sorting: `df.assign(r=...).sort_values(["store", "revenue"], ascending=[True, False])` puts the
ranks next to the values in order, where ties are easy to see.
