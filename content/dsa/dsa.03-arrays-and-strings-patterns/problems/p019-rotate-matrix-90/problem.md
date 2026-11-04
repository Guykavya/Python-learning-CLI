# Rotate a square grid by 90 degrees

Rotate an `n x n` grid **clockwise** by 90 degrees, `k` times, and print it.

After one clockwise turn, the first row becomes the last column (read from top to bottom), and the first column
becomes the first row (read from right to left). A neat way to do one turn **in place**:

1. **transpose**: swap `g[i][j]` with `g[j][i]` for every pair with `j > i`;
2. **reverse each row**.

`k` can be as large as 10^9. Four turns bring the grid back to the start, so only `k % 4` turns matter.

## Input

- Line 1: `n k`.
- Next `n` lines: `n` integers each.

## Output

`n` lines: the rotated grid, values separated by spaces.

## Example

Input:

```
3 1
1 2 3
4 5 6
7 8 9
```

Output:

```
7 4 1
8 5 2
9 6 3
```

The first row `1 2 3` is now the last column. With `k = 2` the output would be the grid upside down and mirrored
(`9 8 7` / `6 5 4` / `3 2 1`); with `k = 4` it would be unchanged.

## Constraints

- `1 <= n <= 500`
- `0 <= k <= 10^9`
