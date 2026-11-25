## Approach

Count edges. For a sorted `edges`, the bin number is just "how many edges are to the left of the value":

| value | edges `<=` v | edges `<` v |
|---|---|---|
| 5 | 0 | 0 |
| 10 | 1 | 0 |
| 15 | 1 | 1 |
| 20 | 2 | 1 |
| 30 | 3 | 2 |
| 35 | 3 | 3 |

- Line 1, `digitize` default (`right=False`): count of edges `<=` v → `[0, 1, 1, 2, 3, 3]`.
- Line 2, `right=True`: count of edges `<` v → `[0, 0, 1, 1, 2, 3]`.
- Line 3, `searchsorted` left: insert before equal elements = count of edges `<` v → same as line 2.
- Line 4, `searchsorted` right: insert after equal elements = count of edges `<=` v → same as line 1.
- Line 5: label by bin number of line 1 → `['low', 'mid', 'mid', 'high', 'top', 'top']`.
- Line 6: counts of the bin numbers of line 2: two 0s, two 1s, one 2, one 3 → `[2, 2, 1, 1]`.

## Code

The expected output is in `expected.txt`, produced by running the program.

## Complexity

Both functions use binary search: O(log k) per value for k edges, O(n log k) in all.

## Another way

`np.digitize(v, edges, right=False)` is `np.searchsorted(edges, v, side="right")` and `right=True` is `side="left"`: the names point in opposite directions, which is the whole trap. For a histogram, `np.histogram` (Ch. 14.4) uses yet another rule: every bin is half-open `[a, b)` except the **last**, which is closed `[a, b]`.
