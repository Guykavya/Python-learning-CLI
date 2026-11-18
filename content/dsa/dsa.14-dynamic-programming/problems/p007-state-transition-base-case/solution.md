## Approach

Fill the boxes from left to right. Each new box is the sum of at most three earlier boxes, so every value you need is already on paper.

## Expected output

```text
f[0] = 1  (base case)
f[1] = f[0] = 1
f[2] = f[1] = 1
f[3] = f[2] + f[0] = 2
f[4] = f[3] + f[1] + f[0] = 4
f[5] = f[4] + f[2] + f[1] = 6
f[6] = f[5] + f[3] + f[2] = 9
f[7] = f[6] + f[4] + f[3] = 15
f[8] = f[7] + f[5] + f[4] = 25
table: [1, 1, 1, 2, 4, 6, 9, 15, 25]
answer: 25
```

## Why

| i | terms used | sum |
|---|---|---|
| 1 | f[0] | 1 |
| 2 | f[1] | 1 |
| 3 | f[2] + f[0] | 1 + 1 = 2 |
| 4 | f[3] + f[1] + f[0] | 2 + 1 + 1 = 4 |
| 5 | f[4] + f[2] + f[1] | 4 + 1 + 1 = 6 |
| 6 | f[5] + f[3] + f[2] | 6 + 2 + 1 = 9 |
| 7 | f[6] + f[4] + f[3] | 9 + 4 + 2 = 15 |
| 8 | f[7] + f[5] + f[4] | 15 + 6 + 4 = 25 |

Check `f[4] = 4`: `1111`, `13`, `31`, `4`. Check `f[5] = 6`: `11111`, `113`, `131`, `311`, `14`, `41`.

Answers to the questions: `f[0] = 1` counts the empty sequence; with 0, every sum would be 0. The guard `if i - s >= 0` is the "no steps below the ground" base case: those terms contribute nothing.

## Another way

Write the recursion `ways(i) = ways(i-1) + ways(i-3) + ways(i-4)` with `ways(0) = 1` and `ways(negative) = 0`, and evaluate `ways(8)` with a notebook. You get the same nine numbers, filled in the order the recursion first finishes them, which is also `0, 1, 2, ..., 8`.
