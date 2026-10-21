## Hint 1

For a given `i`, the inner loop runs once for each of `j = 1, 2, 4, ...` that is `<= i`. So `i = 1` takes 1 step,
`i = 2, 3` take 2, `i = 4..7` take 3, `i = 8..15` take 4. (This is the number of binary digits of `i`.)

## Hint 2

The group of numbers that take `k` steps runs from `2^(k-1)` to `2^k - 1`, and it has `2^(k-1)` members. So it adds
`k * 2^(k-1)` to the count, unless it is the last group, which is cut off at `n`.

## Hint 3

```
count = 0, k = 1, low = 1
while low <= n:
    high = smaller of n and 2 * low - 1
    count += k * (high - low + 1)
    low = low * 2, k = k + 1
```
