# Count inversions

An **inversion** is a pair of positions `i < j` with `a[i] > a[j]` (strictly greater). Count the inversions of a list in `O(n log n)` by adding a counter to merge sort.
The idea: while merging two sorted halves, every time you take a value from the **right** half, it is smaller than all values still waiting in the left half,
so it forms an inversion with each of them.

## Input

- Line 1: `n`.
- Line 2: `n` integers.

## Output

One integer: the number of inversions (it can be as large as about `2 * 10^10`).

## Constraints

- `1 <= n <= 200000`
- `-10^9 <= a[i] <= 10^9`

Equal values are **not** inversions.

## Example

Input:

```
5
2 4 1 3 5
```

Output:

```
3
```
