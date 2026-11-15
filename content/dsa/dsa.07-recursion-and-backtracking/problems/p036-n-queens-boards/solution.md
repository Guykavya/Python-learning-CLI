## Approach

The same search as in chapter section 11. At the leaves, convert the column list into `n` strings. Every leaf is a valid board because every placement was checked when it was made.

## Code

```python
def solve_n_queens(n):
    solutions = []
    cols_of = []
    cols, diag, anti = set(), set(), set()

    def go(r):
        if r == n:
            solutions.append(["." * c + "Q" + "." * (n - c - 1) for c in cols_of])
            return
        for c in range(n):
            if c in cols or (r - c) in diag or (r + c) in anti:
                continue
            cols_of.append(c); cols.add(c); diag.add(r - c); anti.add(r + c)
            go(r + 1)
            cols_of.pop(); cols.remove(c); diag.remove(r - c); anti.remove(r + c)

    go(0)
    return solutions
```

## Complexity

As for counting, plus `O(n^2)` to build each board.

## Another way

Keep a real board (list of lists of characters), set `board[r][c] = "Q"` when choosing and back to `"."` when un-choosing, and record `["".join(row) for row in board]` at the leaves.
