## Hint 1

Do pass 1 by hand: compare 5 and 1 (swap), then 5 and 4, 5 and 2, 5 and 8. The 5 travels right until it meets the 8.

## Hint 2

Each swap adds 1 to `swaps` and prints nothing by itself: the print happens once per pass, after the inner loop.

## Hint 3

There are `len(a) - 1 = 4` passes, so exactly 4 `pass` lines, then the `sorted:` line.
