## Approach

Connect halving to logarithms (`2^20` is about a million), then explain that the discard step relies on the order of the data, and compare total costs for one query and for many.

## Model answer

See `answer.md`. Compare it with yours point by point.

## What to check

- `2^20 = 1,048,576`, so 20 probes (21 counting the last check) for a million; 30 for a billion.
- Doubling the size adds exactly one probe.
- An unsorted example, e.g. `[5, 1, 4, 2, 3]` searching 1: the middle 4 is greater than 1, so the search goes left, finds 5 and misses... or similar, with the reasoning shown.
- One query: sorting `O(n log n)` is worse than a scan `O(n)`. Many queries: `O(n log n + q log n)` beats `O(q n)`.
- The order: if `a[mid] < x` then everything left of `mid` is also `< x` and can be ignored.
