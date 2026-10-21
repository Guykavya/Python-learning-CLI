## Approach

Every subset either excludes or includes the first item. The subsets that exclude it are exactly
the subsets of the rest; those that include it are the same subsets with the first item put in
front. Trust the recursive call for the rest, then build both halves. With `max_size`, a subset
may take the first item only if it has room left, so too-big subsets are never built.

## Code

```python
def subsets(items, *, max_size=None):
    """Return every subset of items (as lists, in item order), optionally only up to max_size items."""
    if not items:
        return [[]]
    first = items[0]
    without = subsets(items[1:], max_size=max_size)
    with_first = [[first] + s for s in without if max_size is None or len(s) < max_size]
    return without + with_first
```

## Complexity

O(n × 2ⁿ) time and output size; recursion depth n.

## Another way

Counting in binary: for each number `mask` from 0 to 2ⁿ - 1, item i is in the subset when bit i
of `mask` is set (`mask >> i & 1`). No recursion, but the recursive version explains *why* there
are 2ⁿ subsets: each item doubles the count.
