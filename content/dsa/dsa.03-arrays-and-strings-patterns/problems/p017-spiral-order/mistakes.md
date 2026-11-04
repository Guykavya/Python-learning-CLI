- No re-check before the bottom row and left column. On a single row `1 2 3` the loop walks the top row, then the
  "bottom row" (the same row) backwards, printing `1 2 3 2 1`.
- Using `r` for both dimensions: works on square grids only.
- Off by one in the backward ranges: `range(right, left - 1, -1)` includes `left`; `range(right, left, -1)` misses it.
- Shrinking a boundary before walking its side, so the first or last cell of a side is skipped.
- Stopping when the count of printed cells reaches `r * c` but without the checks: the count is right, the order may
  not be.
