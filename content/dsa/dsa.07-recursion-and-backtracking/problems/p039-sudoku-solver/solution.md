## Approach

Backtracking over the empty cells, with the three set families giving the allowed digits in `O(1)` per test. On success the recursion returns `True` all the way up without undoing, so the board stays filled. Invalid givens are caught while building the sets.

## Code

```python
def solve_sudoku(board):
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    empties = []
    for r in range(9):
        for c in range(9):
            d = board[r][c]
            if d == 0:
                empties.append((r, c))
                continue
            b = (r // 3) * 3 + c // 3
            if d in rows[r] or d in cols[c] or d in boxes[b]:
                return None                          # the givens already clash
            rows[r].add(d); cols[c].add(d); boxes[b].add(d)

    def go(k):
        if k == len(empties):
            return True
        r, c = empties[k]
        b = (r // 3) * 3 + c // 3
        for d in range(1, 10):
            if d in rows[r] or d in cols[c] or d in boxes[b]:
                continue
            board[r][c] = d
            rows[r].add(d); cols[c].add(d); boxes[b].add(d)           # choose
            if go(k + 1):
                return True                                           # keep the board
            board[r][c] = 0
            rows[r].remove(d); cols[c].remove(d); boxes[b].remove(d)  # un-choose
        return False

    return board if go(0) else None
```

## Complexity

Exponential in the number of empty cells in the worst case; in practice a few thousand to a few tens of thousands of calls for ordinary puzzles. Picking the cell with the fewest options at every step (section 12) usually cuts that to a few hundred.

## Another way

"Most constrained cell first": at every call, choose the empty cell with the fewest allowed digits. A cell with zero options makes the branch fail at once, which is the strongest pruning for Sudoku.
