# Sudoku solver

Write `solve_sudoku(board)` for a 9x9 board (list of 9 lists of 9 ints, `0` = empty). Fill the empty cells so that every row, column and 3x3 box contains the digits 1 to 9 exactly once, keeping every given digit. Return the solved board (a 9x9 list of lists; you may fill `board` in place and return it). If there is **no** solution, return `None`.

The givens themselves may already break the rules (for example two 5s in one row). Such a board has no solution: return `None`.

## Example

```python
>>> easy = "530070000600195000098000060800060003400803001700020006060000280000419005000080079"
>>> board = [[int(ch) for ch in easy[r * 9:(r + 1) * 9]] for r in range(9)]
>>> solved = solve_sudoku(board)
>>> solved[0]
[5, 3, 4, 6, 7, 8, 9, 1, 2]
```

## Constraints

- The tests use an easy and a harder puzzle (each with exactly one solution), and boards with no solution. Each must finish within a few seconds.
- Work on the **first** empty cell in row-major order, or on the most constrained one (chapter section 12). Both are fast enough.

## Think about

Use three families of sets (`rows`, `cols`, `boxes`) as in chapter section 12, filled from the givens. When the recursion **succeeds**, do not undo anything: you want to keep the filled board. When it fails, undo the digit and try the next one.
