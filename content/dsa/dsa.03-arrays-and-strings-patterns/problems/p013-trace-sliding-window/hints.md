## Hint 1

The first window is `a[0:3] = [4, 2, -1]` with sum 5. For `r = 3`, the entering element is `a[3] = 3` and the
leaving one is `a[0] = 4`. So the new sum is `5 + 3 - 4`.

## Hint 2

The slice `a[r - k + 1:r + 1]` is the window **after** the slide: for `r = 3` it is `a[1:4]`. When `-1` leaves,
`s - (-1)` adds 1.

## Hint 3

The sums are 5, 4, 7, 2, 0. `best` changes only when a sum is strictly bigger than the best so far.
