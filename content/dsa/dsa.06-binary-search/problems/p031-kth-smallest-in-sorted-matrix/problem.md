# Kth smallest in a sorted matrix

An `n x n` matrix has **every row sorted ascending and every column sorted ascending**. Values may repeat. Print the `k`-th smallest value in the whole matrix (counting duplicates, 1-based: `k = 1` is the minimum).

The rows are not globally sorted, so you cannot index the answer. Instead, binary search on the **value**: for a candidate `v`, count how many entries are `<= v` using a *staircase walk* (start at the bottom-left corner: if the entry is `<= v`, the whole column above it counts and you move right; otherwise move up). The count is non-decreasing in `v`.
`sorted`, `.sort` and `heapq` are not allowed.

## Input

- Line 1: `n k`. Then `n` lines with `n` integers each.

## Output

One integer.

## Constraints

- `1 <= n <= 700`, `1 <= k <= n * n`, `-10^9 <= value <= 10^9`

## Example

Input:

```
3 8
1 5 9
10 11 13
12 13 15
```

Output:

```
13
```

(The values in order: 1 5 9 10 11 12 13 13 15; the 8th is 13.)
