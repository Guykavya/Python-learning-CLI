## Hint 1

For each template, write the loop condition in words: "while the range still contains candidates". How many candidates does `[lo, hi]` hold? How many does `[lo, hi)` hold?

## Hint 2

Invariant of the closed template: "if the target exists it is inside `[lo, hi]`". Half-open: "the answer is inside `[lo, hi]` and `hi` is always a valid answer", where `hi = n` means "none". The shrink template ends with `lo == hi` as the single remaining candidate.

## Hint 3

With `lo = 3, hi = 4`: `(3 + 4) // 2 = 3`, and `lo = mid` leaves `lo = 3` again: no progress. Rounding up gives `mid = 4`.
