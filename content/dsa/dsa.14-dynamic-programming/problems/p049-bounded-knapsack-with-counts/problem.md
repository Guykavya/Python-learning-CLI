# Bounded knapsack with counts

A shop has several **kinds** of items. Kind `k` is described by `(weight, value, count)`: every copy weighs `weight`, is worth `value`, and there are only `count` copies. Your bag holds total weight `W`. Write `bounded_knapsack(items, W)` that returns the largest total value you can carry.

This sits between the two knapsacks of chapter sections 10 and 11: each kind is not used "at most once" (0/1) nor "any number of times" (unbounded), but **at most `count` times**.

## Example

```python
>>> bounded_knapsack([(2, 3, 2), (3, 4, 1)], 7)    # two of the first, one of the second
10
>>> bounded_knapsack([(1, 5, 3)], 10)               # only 3 copies exist
15
>>> bounded_knapsack([(4, 10, 5)], 3)               # nothing fits
0
>>> bounded_knapsack([(1, 2, 0), (2, 3, 1)], 5)     # a kind with count 0
3
```

## Constraints

- `0 <= len(items) <= 100`, `1 <= weight <= 100`, `0 <= value <= 1000`, `0 <= count <= 1000`, `0 <= W <= 5000`.
- The big test has 100 kinds with up to 1000 copies each and `W = 5000`. Turning every copy into its own 0/1 item is correct but makes up to 100,000 items: about `3 * 10**8` steps, too slow. Aim for `O(W * sum of log2(count + 1))`.

## Think about

Instead of 1000 separate copies, could you offer the knapsack a few **bundles** (1 copy, 2 copies, 4 copies, ...) so that every number of copies from 0 to `count` can be made by choosing some bundles, each at most once? Then each bundle is an ordinary 0/1 item.
