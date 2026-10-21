## Hint 1

For a fixed `i`, how many values does `range(i + 1, n)` have? Write that count for `i = 0, 1, 2, ...`.

## Hint 2

The counts are `n - 1, n - 2, ..., 1, 0`. Their sum is the same as `0 + 1 + 2 + ... + (n - 1)`.
You may remember the formula for `1 + 2 + ... + m`.

## Hint 3

`1 + 2 + ... + m = m * (m + 1) / 2`. Here `m = n - 1`, so the answer is `n * (n - 1) / 2`.
In Python write it with `//` so the result stays an exact integer.
