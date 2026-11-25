# Histogram counts

Chapter section 14.1. A histogram counts how many values fall in each of `bins` equal-width intervals. Write `histogram_counts(values, bins, low=None, high=None)` returning `(rows, outside)`:

- `low` and `high` default to `min(values)` and `max(values)`. The width is `(high - low) / bins`.
- `rows` is a list of `bins` tuples `(left, right, count)`; `left = low + i * width`, `right = low + (i + 1) * width` (the last `right` is exactly `high`).
- Bins are **half-open**, `left <= x < right`, **except the last bin, which also includes `high`**: the maximum value must land in the last bin, not disappear.
- Values below `low` or above `high` are not counted in any bin; `outside` is how many there were.
- `bins < 1` raises `ValueError`; an empty list without an explicit range raises `ValueError`. If `low == high` (width 0) every value in range goes into the first bin.

Use bin counts and ranges whose width is exactly representable in the tests (the tests use whole numbers).

## Example

```python
histogram_counts([1, 2, 2, 3, 4, 10], bins=3)
# ([(1.0, 4.0, 4), (4.0, 7.0, 1), (7.0, 10.0, 1)], 0)
```

The 4 falls in the second bin (`4 <= x < 7`), and the 10 (the maximum) in the last bin.
