# Count occurrences of x

A sorted list (duplicates allowed) and several queries. For each query print **how many times** it occurs in the list.

The count is `upper_bound(x) - lower_bound(x)`. Write both searches by hand (a small helper function is fine). `bisect`, `count`, `index` and `in` are not allowed.

## Input

- Line 1: `n`. Line 2: `n` integers in non-decreasing order.
- Line 3: `q`. Line 4: `q` integers.

## Output

`q` lines, one count each (0 if absent).

## Constraints

- `1 <= n <= 100000`, `1 <= q <= 100000`
- `-10^9 <= a[i], x <= 10^9`

## Example

Input:

```
8
1 2 2 2 5 7 7 9
4
2 7 3 9
```

Output:

```
3
2
0
1
```
