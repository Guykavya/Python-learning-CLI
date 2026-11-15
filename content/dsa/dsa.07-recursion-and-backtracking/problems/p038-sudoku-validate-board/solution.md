## Approach

Every filled cell belongs to one row, one column and one box. Keep the set of digits seen in each of the 27 units; a digit that is already in one of its three sets is a repeat.

## Code

```python
def is_valid_sudoku(board):
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    for r in range(9):
        for c in range(9):
            d = board[r][c]
            if d == 0:
                continue
            b = (r // 3) * 3 + c // 3
            if d in rows[r] or d in cols[c] or d in boxes[b]:
                return False
            rows[r].add(d)
            cols[c].add(d)
            boxes[b].add(d)
    return True
```

## Complexity

81 cells, `O(1)` work each.

## Another way

Three helper loops, one per unit kind, each building a list of the non-zero digits of the unit and comparing its length with the size of its set. Slower to write but easy to debug, because a failing check tells you which unit failed.
