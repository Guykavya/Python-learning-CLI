## Hint 1

Store the board as a list of three strings (or lists). `board[r][c]` is one cell.

## Hint 2

Build a list of all 8 lines: the 3 rows, the 3 columns (`[board[r][c] for r in range(3)]`), and
the 2 diagonals.

## Hint 3

A line is won by X if all its cells are `X`: `line == ["X", "X", "X"]`, or `all(ch == "X" for ch in line)`.
