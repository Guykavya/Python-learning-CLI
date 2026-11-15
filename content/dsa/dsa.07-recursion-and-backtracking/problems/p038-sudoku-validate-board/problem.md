# Sudoku: validate a board

A Sudoku board is a list of 9 rows, each a list of 9 integers; `0` means an empty cell, `1 .. 9` a filled one. Write `is_valid_sudoku(board)` that returns `True` if no **row**, no **column** and no **3x3 box** contains the same digit twice, and `False` otherwise. Empty cells are ignored, so a partly filled board can be valid. (Whether the board can be completed does not matter here.)

The boxes are numbered as in chapter section 12: `box = (r // 3) * 3 + c // 3`.

## Example

```python
>>> board = [[0] * 9 for _ in range(9)]
>>> is_valid_sudoku(board)
True
>>> board[0][0] = board[0][8] = 5      # two 5s in row 0
>>> is_valid_sudoku(board)
False
```

## Constraints

- `board` is always 9x9 with values `0 .. 9`. Do not change it.

## Think about

You can check the three kinds of units in three separate loops, or in **one** pass over the cells with 27 sets (9 rows, 9 columns, 9 boxes), as the solver of section 12 does.
