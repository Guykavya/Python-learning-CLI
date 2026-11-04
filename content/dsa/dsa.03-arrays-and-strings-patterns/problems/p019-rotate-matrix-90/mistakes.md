- Transposing by swapping every pair `(i, j)`, not only `j > i`: each pair is swapped twice and nothing changes.
- Reversing the **order of the rows** instead of each row after the transpose: that turns the grid counter-clockwise.
- Looping `k` times without `% 4`: for `k = 10^9` that is a billion turns.
- Copying with `h = g` and writing into `h` while reading from `g`: they are the same list, so values get
  overwritten before they are read. Either work in place with swaps or build a truly new grid.
