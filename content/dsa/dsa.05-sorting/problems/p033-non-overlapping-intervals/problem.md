# Fewest intervals to remove

Given `n` half-open intervals `[l, r)`, remove as few as possible so that the remaining ones do **not overlap**. Intervals that only touch (`[1, 2)` and `[2, 3)`) do not overlap.
Print the minimum number of intervals to remove.

## Input

- Line 1: `n`.
- Next `n` lines: `l r` with `l < r`.

## Output

One integer.

## Constraints

- `0 <= n <= 200000`
- `-10^9 <= l < r <= 10^9`

Equivalent view: keep the **largest** possible set of pairwise non-overlapping intervals; the answer is `n` minus its size.

## Example 1

Input:

```
4
1 2
2 3
3 4
1 3
```

Output:

```
1
```

## Example 2

Input:

```
3
1 2
1 2
1 2
```

Output:

```
2
```
