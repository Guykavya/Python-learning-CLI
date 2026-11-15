## Approach

One queen per row removes the row conflicts by construction. The three sets answer "is this column / diagonal / anti-diagonal taken?" in `O(1)`. Each call returns how many complete placements exist below it; the leaves at `r == n` count 1.

## Code

```python
def total_n_queens(n):
    cols, diag, anti = set(), set(), set()

    def go(r):
        if r == n:
            return 1
        count = 0
        for c in range(n):
            if c in cols or (r - c) in diag or (r + c) in anti:
                continue
            cols.add(c); diag.add(r - c); anti.add(r + c)            # choose
            count += go(r + 1)                                     # explore
            cols.remove(c); diag.remove(r - c); anti.remove(r + c)  # un-choose
        return count

    return go(0)
```

## Complexity

Far below `n^n` thanks to pruning; roughly `O(n!)` in the worst case. Depth `n`.

## Another way

Bit masks instead of sets (chapter section 11, "A faster way"): the free columns of the next row are `~(cols | diag | anti) & full`, and the diagonals shift by one bit per row. Symmetry halves the work again: count the placements with the first queen in the left half and double.
