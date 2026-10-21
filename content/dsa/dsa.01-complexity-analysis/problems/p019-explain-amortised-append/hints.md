## Hint 1

List the appends that cause a copy when the capacity doubles from 1: which append numbers are they, and how many
items does each copy?

## Hint 2

`1 + 2 + 4 + ... + 2^k = 2^(k+1) - 1`. Compare that with `n` when `2^k` is the largest power of two below `n`.
For the "+10" rule the copies are 10, 20, 30, ...: an arithmetic sum, like the nested-loop triangle.

## Hint 3

For `insert(0, x)`: where does each existing item have to go? For the timings, compute the ratio of the two
times in each column and compare it with 10 (linear) and 100 (quadratic).
