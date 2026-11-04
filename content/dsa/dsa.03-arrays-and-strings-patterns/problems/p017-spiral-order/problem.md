# Spiral order of a grid

Walk an `r x c` grid in **spiral order**: along the top row from left to right, down the right column, along the
bottom row from right to left, up the left column, and then the same again one ring further in, until every cell has
been visited exactly once. Print the values in that order.

Keep four boundaries: `top`, `bottom` (row numbers) and `left`, `right` (column numbers). After walking a side,
move its boundary one step inwards. Be careful with grids that are not square, and with a single row or column:
no cell may be printed twice.

## Input

- Line 1: `r c`.
- Next `r` lines: `c` integers each.

## Output

One line: all `r * c` values in spiral order, separated by spaces.

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
1 2 3 4 8 12 11 10 9 5 6 7
```

Top row `1 2 3 4`, right column `8 12`, bottom row backwards `11 10 9`, left column upwards `5`. The inner ring is just
`6 7`.

## Constraints

- `1 <= r, c` and `r * c <= 250000`
