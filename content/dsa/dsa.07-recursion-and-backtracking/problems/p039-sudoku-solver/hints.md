## Hint 1

Build the sets from the givens first. While doing so, if a given digit is already in its row, column or box set, the board has no solution.

## Hint 2

Make a list of the empty cells. `go(k)` fills empty cell number `k`: for each digit not in its three sets, place it (grid and sets), and if `go(k + 1)` returns `True`, return `True` at once. Otherwise remove it again. If no digit works, return `False`.

## Hint 3

```
def go(k):
    if k == len(empties): return True
    r, c = empties[k]; b = (r // 3) * 3 + c // 3
    for d in 1..9:
        if d in rows[r] or d in cols[c] or d in boxes[b]: continue
        place d; if go(k + 1): return True; remove d
    return False
return board if go(0) else None
```
