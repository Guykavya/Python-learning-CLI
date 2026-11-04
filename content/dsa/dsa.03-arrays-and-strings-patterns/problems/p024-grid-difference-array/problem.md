# Rectangle updates with a 2D difference array

A grid of `r` rows and `c` columns starts full of zeros. Then `q` updates arrive. Update `r1 c1 r2 c2 v` adds `v`
to every cell `(i, j)` with `r1 <= i <= r2` and `c1 <= j <= c2` (rows and columns numbered from 1, corners
included). Print the grid after all updates.

Touching every cell of every rectangle can cost `250000` steps per update. Instead, mark each update at
**four corners** of a difference grid, and turn the marks into values with **one** 2D prefix sum at the end.

## Input

- Line 1: `r c q`.
- Next `q` lines: `r1 c1 r2 c2 v`, with `r1 <= r2` and `c1 <= c2`.

## Output

`r` lines with `c` integers each, separated by single spaces: the final grid.

## Example

Input:

```
3 4 3
1 1 2 3 5
2 2 3 4 -2
3 1 3 1 7
```

Output:

```
5 5 5 0
5 3 3 -2
7 -2 -2 -2
```

The first update adds 5 to rows 1–2, columns 1–3. The second adds -2 to rows 2–3, columns 2–4. The third adds 7
to the single cell `(3, 1)`.

## Constraints

- `1 <= r, c <= 500`
- `1 <= q <= 100000`
- `-10^9 <= v <= 10^9`

Use `input()` without a prompt message.
