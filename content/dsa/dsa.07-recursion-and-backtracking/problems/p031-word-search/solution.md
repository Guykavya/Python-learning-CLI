## Approach

Backtracking on the grid. The path state is "which cells are in use"; marking a cell with `"#"` stores it in the board itself, so no extra set is needed. The un-choose step restores the letter, also when the search succeeded, so the board is unchanged at the end.

## Code

```python
def exist(board, word):
    rows, cols = len(board), len(board[0])

    def go(r, c, k):
        if k == len(word):
            return True
        if not (0 <= r < rows and 0 <= c < cols) or board[r][c] != word[k]:
            return False
        saved = board[r][c]
        board[r][c] = "#"                          # choose: mark used
        found = (go(r + 1, c, k + 1) or go(r - 1, c, k + 1) or
                 go(r, c + 1, k + 1) or go(r, c - 1, k + 1))
        board[r][c] = saved                        # un-choose: restore
        return found

    return any(go(r, c, 0) for r in range(rows) for c in range(cols))
```

## Complexity

From each of the `R * C` starts, each step has at most 3 new directions: `O(R * C * 3^L)` in the worst case for a word of length `L`. Depth `L`.

## Another way

Keep a `set` of visited `(r, c)` instead of writing into the board; add before the recursive calls, remove after. Prunings from the chapter: give up at once if the board does not contain enough of some letter, and start from the rarer end of the word.
