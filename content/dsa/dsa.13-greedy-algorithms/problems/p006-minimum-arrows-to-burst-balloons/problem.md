# Minimum arrows to burst balloons

Balloons are taped to a wall. Seen from below, each balloon covers the stretch `[x_start, x_end]` of the x-axis. An arrow shot straight up at position `x` bursts **every** balloon with `x_start <= x <= x_end`, and keeps flying. Write `min_arrows(balloons)`: the fewest arrows that burst all balloons.

Rules (chapter section 5):

- Each balloon is a pair `(x_start, x_end)` of integers with `x_start <= x_end`, as a tuple or a list. The list is not sorted.
- Balloons are **closed** intervals: two balloons that **touch** at one point, like `(1, 2)` and `(2, 3)`, can be burst by **one** arrow at `x = 2`.
- Return an `int`. No balloons need `0` arrows. Do not change the list you are given.

## Example

```python
>>> min_arrows([(10, 16), (2, 8), (1, 6), (7, 12)])
2
>>> min_arrows([(1, 2), (3, 4), (5, 6), (7, 8)])
4
>>> min_arrows([(1, 2), (2, 3), (3, 4), (4, 5)])
2
```

In the first example, arrows at 6 and 12 are enough. In the last one, arrows at 2 and 4 each hit two touching balloons.

## Constraints

- `0 <= len(balloons) <= 10**5`. Aim for `O(n log n)`.

## Think about

The first arrow must hit the balloon that ends first. Where is the best place to shoot it: at that balloon's start, its middle, or its **end**? Why is shooting further right never worse?
