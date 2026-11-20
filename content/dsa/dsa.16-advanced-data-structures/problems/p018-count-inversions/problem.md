# Count inversions

A music app compares a user's ranking of songs with the official chart. The distance between two rankings is the number of **inversions**: pairs `i < j` with `a[i] > a[j]`. Write `count_inversions(a)` using a Fenwick tree and coordinate compression (chapter section 12).

## Example

```python
>>> count_inversions([40, 10, 30, 10, 20])
6
>>> count_inversions([1, 2, 3, 4]), count_inversions([4, 3, 2, 1]), count_inversions([2, 2, 2])
(0, 6, 0)
>>> count_inversions([])
0
```

## Constraints

- Up to 2 * 10**5 numbers from `-10**9` to `10**9`, duplicates allowed (equal values are **not** an inversion).
- `O(n log n)`. Checking all pairs is `2 * 10**10` comparisons.

## Think about

1. Scanning left to right, how many inversions end at the current element `x`? Which earlier elements count?
2. Why can't the Fenwick tree have one cell per **value**? What do you replace the values with?
3. Equal values: should you count earlier elements `>= x` or `> x`?
