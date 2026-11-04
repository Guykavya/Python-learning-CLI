- Looping `while i <= j`: then `i == j` pairs an element with itself, so `[5]` with target 10 wrongly finds `1 1`.
- Moving the wrong pointer: when the sum is too small, moving `j` left makes it even smaller.
- Printing 0-based positions. The output is 1-based.
- Two nested loops over all pairs: correct, but far too slow for 200000 elements.
- Starting the inner search for `j` from the left (`j = i + 1, i + 2, ...`): with duplicates you find a different
  pair than the pinned one (the largest `j`).
