# nCr from Pascal's triangle

`C(n, r)` ("n choose r") is the number of ways to pick `r` items out of `n`, ignoring order. For example
`C(4, 2) = 6`. Pascal's triangle builds all of them with one rule:

```
C(n, 0) = C(n, n) = 1
C(n, r) = C(n - 1, r - 1) + C(n - 1, r)
```

Row `n` of the triangle holds `C(n, 0), C(n, 1), ..., C(n, n)`. Build the rows once (row by row, each
from the previous row), then answer the queries by looking up the table. If `r > n`, the answer is 0.

Do not use `math.comb`. Do not compute each answer by recursion with no memory: the same sub-problems are solved again and again,
and `C(60, 30)` would take longer than your lifetime.

## Input

- Line 1: `q`.
- The next `q` lines: two integers `n r`.

## Output

`q` lines: `C(n, r)` as an exact integer.

## Example

Input:

```
4
5 2
4 0
6 6
3 5
```

Output:

```
10
1
1
0
```

## Constraints

- `1 <= q <= 1000`
- `0 <= n <= 60`, `0 <= r <= 60`

(`C(60, 30)` is 118264581564861424, about 1.2 * 10^17, so exact values still fit even in a signed 64-bit integer.)

Use `input()` without a prompt message.
