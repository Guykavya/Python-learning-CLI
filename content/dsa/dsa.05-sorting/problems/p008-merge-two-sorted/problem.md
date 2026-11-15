# Merge two sorted lists

You are given two lists that are already sorted in non-decreasing order. Print the single sorted list that contains all values of both.
Do it with **two pointers** in `O(n + m)`; do not sort the combined list. `sorted()`, `.sort()`, `heapq` and `bisect` are not allowed:
the tests read your source. This is the merge step you will reuse inside merge sort.

## Input

- Line 1: `n m`.
- Line 2: `n` integers (sorted).
- Line 3: `m` integers (sorted). A line is empty when its count is 0.

## Output

One line with the merged list. When `n + m = 0` print nothing.

## Constraints

- `0 <= n, m <= 200000`

## Example

Input:

```
3 4
1 4 7
2 4 9 10
```

Output:

```
1 2 4 4 7 9 10
```
