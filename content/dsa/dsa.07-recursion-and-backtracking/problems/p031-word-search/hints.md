## Hint 1

Try every cell as a start. From a cell that matches `word[k]`, the rest `word[k+1:]` must be found starting at one of the four neighbours.

## Hint 2

`go(r, c, k)` returns `True` if `word[k:]` can be spelled starting at `(r, c)`. Fail if `(r, c)` is off the grid or `board[r][c] != word[k]`. Succeed when `k == len(word)`.

## Hint 3

```
saved = board[r][c]; board[r][c] = "#"           # choose
found = go(r+1,c,k+1) or go(r-1,c,k+1) or go(r,c+1,k+1) or go(r,c-1,k+1)
board[r][c] = saved                              # un-choose, ALWAYS
return found
```
