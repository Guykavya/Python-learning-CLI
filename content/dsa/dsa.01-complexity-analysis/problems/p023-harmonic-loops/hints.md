## Hint 1

For `n = 6`: `i = 1` visits 1, 2, 3, 4, 5, 6 (6 times); `i = 2` visits 2, 4, 6 (3 times); `i = 3` visits 3, 6.
Continue.

## Hint 2

For a given `i`, the multiples of `i` up to `n` are `i, 2i, ..., ki` with `ki <= n`, so there are `n // i` of them.
The total is `n // 1 + n // 2 + ... + n // n`.

## Hint 3

For `n = 30`, group equal values: `30 // i` is 1 for every `i` from 16 to 30 (15 values), 2 for `i` from 11 to 15,
and so on. Only the first few terms need individual work.
