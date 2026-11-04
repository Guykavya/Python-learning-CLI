# Upper bound: how many are at most x

A sorted list (duplicates allowed) and some queries. For each query `x` print how many elements are **less than or equal to** `x`.
Equivalent: the smallest index `i` with `a[i] > x` (or `n`). This is `upper_bound`, and what `bisect_right` returns.

Write it with the half-open template. `bisect`, `count`, `index` and `in` are not allowed.

## Input

- Line 1: `n`. Line 2: `n` integers in non-decreasing order.
- Line 3: `q`. Line 4: `q` integers.

## Output

`q` lines, one number each.

## Constraints

- `1 <= n <= 100000`, `1 <= q <= 100000`
- `-10^9 <= a[i], x <= 10^9`

## Example

Input:

```
6
1 3 3 5 6 9
5
3 4 0 9 1
```

Output:

```
3
3
0
6
1
```
