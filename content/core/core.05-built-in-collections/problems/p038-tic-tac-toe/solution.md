## Approach

Collect all eight lines as lists of three cells, then check each line. Building the lines with
comprehensions keeps the checks simple.

## Code

```python
board = [list(input().strip()) for _ in range(3)]
lines = [row for row in board]
lines += [[board[r][c] for r in range(3)] for c in range(3)]
lines.append([board[i][i] for i in range(3)])
lines.append([board[i][2 - i] for i in range(3)])
if ["X", "X", "X"] in lines:
    print("X wins")
elif ["O", "O", "O"] in lines:
    print("O wins")
elif all(cell != "." for row in board for cell in row):
    print("Draw")
else:
    print("Game on")
```

## Complexity

Constant: there are always 9 cells and 8 lines.
