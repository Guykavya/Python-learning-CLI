# Rectangle sums with 2D prefix sums

You get a grid of integers and many questions of the form "what is the sum of this rectangle?". Adding up
the cells for every question is far too slow when there are `200000` questions. Build a **2D prefix-sum**
table once, then answer each question with four lookups.

Rows and columns are numbered from 1. A query `r1 c1 r2 c2` asks for the sum of every cell `(i, j)` with
`r1 <= i <= r2` and `c1 <= j <= c2` (both corners included).

## Input

- Line 1: `r c` (rows, columns).
- Next `r` lines: `c` integers each.
- Next line: `q`.
- Next `q` lines: `r1 c1 r2 c2`, with `r1 <= r2` and `c1 <= c2`.

## Output

`q` lines: the sum for each query, in order.

## Example

Input:

```
3 4
1 2 3 4
5 6 7 8
9 10 11 12
3
1 1 3 4
2 2 3 3
1 4 2 4
```

Output:

```
78
34
12
```

The second query covers `6 7 / 10 11`, which sums to 34. The third covers the last column of rows 1 and 2:
`4 + 8 = 12`.

## Constraints

- `1 <= r, c <= 500`
- `-10^9 <= value <= 10^9`
- `1 <= q <= 200000`

Use `input()` without a prompt message.
