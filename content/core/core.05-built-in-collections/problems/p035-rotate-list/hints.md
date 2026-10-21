## Hint 1

Rotating right by 2 means the last 2 items move to the front. Which two slices do you join?

## Hint 2

`items[-k:] + items[:-k]`. What goes wrong when `k` is 0, or bigger than the length?

## Hint 3

Reduce `k` first with `k % len(items)` (guard against an empty list). Python's `%` with a
positive divisor always gives a result from 0 to len-1, even for negative `k`.
