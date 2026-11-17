# K smallest pair sums

You get two lists of numbers `a` and `b`, both sorted from small to large, and a number `k`. A **pair** is `(x, y)` with `x` taken from `a` and `y` taken from `b`. There are `len(a) * len(b)` pairs (pairs are told apart by *position*: if `a` contains `1` twice, then `(1, y)` is a different pair for each of the two `1`s).

Write `k_smallest_pairs(a, b, k)`. It returns a list with the `k` pairs that have the **smallest sums** `x + y`, ordered from the smallest sum to the largest (pairs with the same sum may come in any order). If there are fewer than `k` pairs, return all of them. If `a` or `b` is empty, or `k <= 0`, return `[]`. Do not change `a` or `b`.

## Example

```python
>>> k_smallest_pairs([1, 7, 11], [2, 4, 6], 3)
[(1, 2), (1, 4), (1, 6)]
>>> k_smallest_pairs([1, 1, 2], [1, 2, 3], 4)       # sums 2, 2, 3, 3, ...
[(1, 1), (1, 1), (1, 2), (1, 2)]
>>> k_smallest_pairs([1, 2], [3], 10)               # only two pairs exist
[(1, 3), (2, 3)]
```

In the first example, the sums are `3, 5, 7` for the first row; the pair `(7, 2)` has sum `9`, so it comes later. In the second example, the two `1`s of `a` each pair with the `1` of `b` (sum 2) and with the `2` of `b` (sum 3): the answer can be `(1, 1), (1, 1), (1, 2), (1, 2)`. Another correct order of the two sum-3 pairs would also be accepted.

## Constraints

- `a` and `b` up to 100,000 numbers each, and `k` up to 1,000. The two big tests run in a separate process with a 10-second limit and a memory limit. All `len(a) * len(b)` pairs would be 10 billion.
- The tests compare the **sums** and check that every returned pair really exists (once per position pair).

## Think about

Draw the grid: rows are items of `a`, columns are items of `b`, and the cell holds the sum. Along every row and every column the sums grow. After you have taken some cells, which cell can be the next smallest? Why is it enough to start with the first column of the first `k` rows?
