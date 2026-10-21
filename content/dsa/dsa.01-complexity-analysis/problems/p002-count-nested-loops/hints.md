## Hint 1

For each loop, make a small table for `n = 6`: one row per value of `i`, and a column for how many times the
inner loop runs for that `i`. Then add the column.

## Hint 2

For `b`, the inner loop runs 0, 1, 2, ..., n - 1 times. For `c`, it runs n, n - 1, ..., 1 times.
The sum `1 + 2 + ... + m` equals `m * (m + 1) / 2`.

## Hint 3

So `a = n * n`, `b = n * (n - 1) / 2`, `c = n * (n + 1) / 2`, `d = 3 * n`. Put in `n = 1000`.
