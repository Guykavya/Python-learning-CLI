# Parse a grid

A map has `n` rows and `m` columns. Each cell is one of: `.` empty, `#` wall, `S` start, `E` end. There is exactly one `S` and one `E`.

Print `sr sc er ec walls`: the row and column of `S` (1-indexed), the row and column of `E` (1-indexed), and the number of `#` cells.

## Input

The first line holds `n` and `m` (`1 <= n, m <= 1000`). Then `n` lines follow, each a string of `m` characters without spaces. Lines may end with Windows line endings (`\r\n`).

## Output

One line with five integers.

## Example

```text
3 4
#..S
.#..
E..#
```
```text
1 4 3 1 3
```

`S` is at row 1, column 4; `E` is at row 3, column 1; there are three `#` cells.

## The catch

The grid has up to `10**6` cells. Reading it with `input()` row by row is fine for correctness, but a 1000x1000 file must be read and scanned quickly: use `sys.stdin.read().split()`, and avoid a Python double loop over characters where `str.find` and `str.count` do the work in C.
