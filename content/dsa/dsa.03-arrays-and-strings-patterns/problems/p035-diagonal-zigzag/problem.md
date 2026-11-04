# Zigzag diagonal order

Print all cells of an `r x c` grid in **zigzag diagonal order**.

## The rule (exact)

Number rows and columns from 0. Diagonal `d` is the set of cells `(i, j)` with `i + j = d`, for
`d = 0, 1, ..., r + c - 2`. Visit the diagonals in that order:

- when `d` is **even**, walk the diagonal **upward**: from its bottom-left cell to its top-right cell
  (row decreasing, column increasing);
- when `d` is **odd**, walk it **downward**: from its top-right cell to its bottom-left cell
  (row increasing, column decreasing).

Diagonal 0 is just the top-left cell, and the last diagonal is just the bottom-right cell. In a non-square grid,
many diagonals are cut short by an edge: start each one at the first cell that is inside the grid.

## Input

- Line 1: `r c`.
- Next `r` lines: `c` integers each.

## Output

One line: all `r * c` values in zigzag order, separated by single spaces.

## Example

Input:

```
3 4
1 2 3 4
5 6 7 8
9 10 11 12
```

Output:

```
1 2 5 9 6 3 4 7 10 11 8 12
```

Diagonal by diagonal: `1` | `2 5` (down) | `9 6 3` (up) | `4 7 10` (down) | `11 8` (up) | `12`.

A square example: the grid `1 2 3 / 4 5 6 / 7 8 9` gives `1 2 4 7 5 3 6 8 9`.

## Constraints

- `1 <= r, c <= 500`
- `-10^9 <= value <= 10^9`

Use `input()` without a prompt message.
