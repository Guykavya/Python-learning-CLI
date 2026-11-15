# Set matrix zeroes

If a cell of the grid holds `0`, its whole row and its whole column must become `0`. Only zeros that are in the
grid **at the start** count: a cell that becomes 0 because of this rule does not clear its own row and column.

Print the grid after the change.

## Input

- Line 1: `r c` (rows, columns).
- Next `r` lines: `c` integers each.

## Output

`r` lines with `c` integers each, separated by single spaces.

## Example

Input:

```
3 4
1 2 0 4
5 6 7 8
0 1 2 3
```

Output:

```
0 0 0 0
0 6 0 8
0 0 0 0
```

The original zeros are at row 1, column 3 and at row 3, column 1. So rows 1 and 3 and columns 1 and 3 are cleared.
Row 2 keeps `6` and `8`. If the new zero at row 2, column 3 also cleared its row, row 2 would wrongly become all zeros.

## Constraints

- `1 <= r, c <= 500`
- `-10^9 <= value <= 10^9`

Use `input()` without a prompt message.
