# Count reverse pairs

A **reverse pair** is a pair of positions `i < j` with `a[i] > 2 * a[j]` (strictly). Count them in `O(n log n)`.

This is the inversion count of problem p016 with a twist: the condition is `a[i] > 2 * a[j]`, not `a[i] > a[j]`. Because the condition differs from the merge order,
you must **count first** and **merge afterwards**, in two separate passes over the two sorted halves.

## Input

- Line 1: `n`.
- Line 2: `n` integers.

## Output

One integer.

## Constraints

- `1 <= n <= 100000`
- `-2^31 <= a[i] <= 2^31 - 1`

Careful with negative numbers: `2 * a[j]` is smaller than `a[j]` when `a[j] < 0`.

## Example 1

Input:

```
5
1 3 2 3 1
```

Output:

```
2
```

## Example 2

Input:

```
5
2 4 3 5 1
```

Output:

```
3
```
