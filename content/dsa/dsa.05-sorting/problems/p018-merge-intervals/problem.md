# Merge overlapping intervals

You get `n` closed intervals `[l, r]` in any order. Merge all intervals that overlap and print the merged intervals in increasing order.
Two intervals that **touch** (`[1, 2]` and `[2, 3]` share the point 2) **do** merge, so they become `[1, 3]`.

## Input

- Line 1: `n`.
- Next `n` lines: `l r` with `l <= r`.

## Output

One line `l r` per merged interval, ordered by `l`.

## Constraints

- `1 <= n <= 200000`
- `0 <= l <= r <= 10^9`

The key idea: **sort by start first**. After sorting, an interval can only overlap the merged block just before it.

## Example 1

Input:

```
4
1 3
8 10
2 6
15 18
```

Output:

```
1 6
8 10
15 18
```

## Example 2

Input:

```
2
1 2
2 3
```

Output:

```
1 3
```
