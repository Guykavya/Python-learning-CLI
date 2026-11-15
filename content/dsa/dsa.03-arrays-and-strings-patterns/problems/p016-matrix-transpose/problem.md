# Transpose a grid

The **transpose** of a grid swaps rows and columns: row `i` of the original becomes column `i` of the result. The
cell at row `i`, column `j` moves to row `j`, column `i`.

An `r x c` grid (`r` rows, `c` columns) becomes a `c x r` grid. Read the grid and print its transpose.

## Input

- Line 1: `r c`.
- Next `r` lines: `c` integers each.

## Output

`c` lines with `r` integers each, separated by spaces.

## Example

Input:

```
2 3
1 2 3
4 5 6
```

Output:

```
1 4
2 5
3 6
```

The first row `1 2 3` became the first column.

## Constraints

- `1 <= r, c` and `r * c <= 250000`
- `-10^9 <= values <= 10^9`
