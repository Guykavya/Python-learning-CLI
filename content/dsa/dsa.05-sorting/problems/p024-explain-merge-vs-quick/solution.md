## Approach

Compare the two on four axes: where the work is, worst case, memory, stability.

## Model answer

See `answer.md`. Compare it with yours point by point.

## What to check

- Merge sort: easy split, merge is the work, `O(n log n)` always, `O(n)` extra memory, stable.
- Quick sort: partition is the work, nothing to combine, `O(n^2)` worst case, `O(log n)` extra memory, not stable.
- A concrete bad input for last-element pivot: an already sorted list.
- Merge sort for linked lists, external data or stable sorting; quick sort for in-memory arrays of numbers.
