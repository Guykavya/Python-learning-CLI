## Hint 1

Go through the numbers one at a time. For each one write down the loop condition `i * i <= n` with `i = 2`
first. If it is false, the loop body is skipped.

## Hint 2

For 17: `2 * 2 = 4`, `3 * 3 = 9`, `4 * 4 = 16` are all `<= 17`, but `5 * 5 = 25` is not. So the tries are 2, 3, 4.
Each `n % i` is nonzero, so the loop never returns early.

## Hint 3

For 1 and 2 the condition `4 <= n` is false straight away, so `check` prints "no divisor found" and returns
`True`. The last `print` has an extra test `n > 1` that rejects 1.
