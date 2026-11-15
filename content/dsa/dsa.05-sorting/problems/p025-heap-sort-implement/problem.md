# Implement heap sort

Sort a list with **heap sort**, written by hand:

1. **Build** a max-heap in place: for `i` from `n // 2 - 1` down to `0`, `sift_down(i, n)`.
2. **Repeat** for `end = n - 1` down to `1`: swap `a[0]` with `a[end]` (the maximum goes to its final place), then `sift_down(0, end)` on the shrunken heap.

`sift_down(i, size)` swaps `a[i]` with its larger child until the heap rule holds. Write it yourself. `sorted()`, `.sort()`, `heapq` and `bisect` are not allowed:
the tests read your source.

## Input

- Line 1: `n`.
- Line 2: `n` integers.

## Output

The sorted list on one line.

## Constraints

- `1 <= n <= 100000`

## Example

Input:

```
6
3 9 2 1 4 5
```

Output:

```
1 2 3 4 5 9
```
