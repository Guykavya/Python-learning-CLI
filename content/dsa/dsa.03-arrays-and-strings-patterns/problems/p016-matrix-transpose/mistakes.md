- Building the result with `[[0] * r] * c`: all `c` rows are the same list object, so writing one row writes all.
- Mixing up `r` and `c` in a non-square grid: printing `r` lines, or indexing `g[j][i]` past the end.
- In-place transposing a square grid by swapping every `(i, j)` pair: each pair is swapped twice and the grid comes
  back unchanged. Swap only when `j > i`.
- In-place transposing a non-square grid: it cannot work, the shape changes. Build a new grid.
