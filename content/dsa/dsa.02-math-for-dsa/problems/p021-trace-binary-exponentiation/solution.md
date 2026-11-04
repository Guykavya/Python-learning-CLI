## Walkthrough: power(3, 13, 1000)

13 in binary is `1101`. Reading the bits from the lowest: 1, 0, 1, 1.

| pass | base | exp | result (printed) | bit of exp | result after |
|---|---|---|---|---|---|
| 1 | 3 | 13 | 1 | 1 | 3 |
| 2 | 9 | 6 | 3 | 0 | 3 |
| 3 | 81 | 3 | 3 | 1 | 243 |
| 4 | 561 | 1 | 243 | 1 | 323 |

At pass 3 the base is `81^2 = 6561`, which becomes 561. At pass 4, `243 * 561 = 136323`, which becomes 323.
`3^13 = 1594323`, whose last three digits are 323. So the answer is correct.

For `power(2, 10, 1000)`: 10 is `1010`, so the bits from the lowest are 0, 1, 0, 1.

| pass | base | exp | result (printed) | bit of exp | result after |
|---|---|---|---|---|---|
| 1 | 2 | 10 | 1 | 0 | 1 |
| 2 | 4 | 5 | 1 | 1 | 4 |
| 3 | 16 | 2 | 4 | 0 | 4 |
| 4 | 256 | 1 | 4 | 1 | 1024 % 1000 = 24 |

`2^10 = 1024`, so the answer 24 is right.

## Output

```
3 13 1
9 6 3
81 3 3
561 1 243
answer 323
2 10 1
4 5 1
16 2 4
256 1 4
answer 24
answer 1
0 5 1
0 2 0
0 1 0
answer 0
```

## Key ideas

- The loop runs `exp.bit_length()` times: 4 passes for 13 and 10, 0 passes for 0. That is O(log exp).
- `result` collects the `base` values at the passes where the bit is 1. For 13 those are `3^1 * 3^4 * 3^8`.
- With `mod = 1`, every remainder is 0, so the answer is 0 and never an error. Python's `x % 1` is 0.
