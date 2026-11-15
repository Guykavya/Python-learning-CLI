# Integer square root

For each number `n` print `floor(sqrt(n))`: the largest integer `r` with `r * r <= n`.

This is your first **binary search on the answer**: there is no list. The "array" is the set of candidates `0, 1, 2, ..., n`, and the predicate `r * r <= n` is True for small `r` and False for large `r`.
Do not use `math.sqrt`, `math.isqrt`, `pow`, or `** 0.5` (a float loses precision for numbers near 10^18). `** 2` and `r * r` are fine.

## Input

- Line 1: `q`. Next `q` lines: one integer `n` each.

## Output

`q` lines: `floor(sqrt(n))`.

## Constraints

- `1 <= q <= 10000`
- `0 <= n <= 10^18`

## Example

Input:

```
5
0
1
15
16
1000000000000000000
```

Output:

```
0
1
3
4
1000000000
```
