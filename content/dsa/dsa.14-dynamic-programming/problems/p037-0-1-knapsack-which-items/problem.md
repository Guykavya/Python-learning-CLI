# 0/1 knapsack: which items

A shop has a delivery van that carries at most `W` kilograms. Parcel `i` weighs `wt[i]` and pays `val[i]` for delivery. Each parcel goes at most once. Write `pack_van(wt, val, W)` that returns a tuple `(best, items)`:

- `best` is the largest total payment that fits in the van;
- `items` is a **sorted** list of parcel indices that achieves it (total weight `<= W`, total payment `== best`).

The value alone (p036) is not enough for the driver: they need to know which parcels to load. Rebuild the choice from the table (chapter sections 9 and 10, "Which items were taken?").

## Example

```python
>>> pack_van([1, 3, 4, 5], [1, 4, 5, 7], 7)
(9, [1, 2])
>>> pack_van([5, 4, 6, 3], [10, 40, 30, 50], 10)
(90, [1, 3])
>>> pack_van([3], [5], 2)
(0, [])
```

When several sets of parcels give the same `best`, any of them is accepted: the tests check that your list is valid and worth `best`, not that it is one particular list.

## Constraints

- `0 <= len(wt) == len(val) <= 100`; weights from 1 to 1000, payments from 0 to 10**6.
- `0 <= W <= 5000`.
- `O(len(wt) * W)` time.

## Think about

1. You need the full 2-D table, not the one-list version. Why does the one list lose the information you need?
2. Walking back from `f[n][W]`: if `f[i][w] == f[i - 1][w]`, was item `i - 1` needed? And if they differ?
3. After you decide that item `i - 1` was taken, which cell do you move to next?
