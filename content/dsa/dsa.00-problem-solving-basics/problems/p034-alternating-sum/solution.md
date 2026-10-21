## Approach

A loop is correct but useless here: 10^18 steps would take far longer than a lifetime.
So we look for a pattern in **small cases**, worked by hand:

| n | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| sum | 1 | -1 | 2 | -2 | 3 | -3 | 4 | -4 |

- Even `n`: the sum is `-n / 2` (2 -> -1, 4 -> -2, 8 -> -4).
- Odd `n`: the sum is `(n + 1) / 2` (1 -> 1, 5 -> 3, 7 -> 4).

**Why it is true, not just a guess:** pair the terms as `(1 - 2) + (3 - 4) + ...`. Every pair is `-1`.
For even `n` there are `n / 2` pairs, so the sum is `-n / 2`. For odd `n` there are `(n - 1) / 2` pairs
plus a lone `+n`, giving `n - (n - 1) / 2 = (n + 1) / 2`.

Always check a pattern with a reason like this. A pattern that fits 8 cases can still be wrong for case 9.

## Trace

Checking the formula against a slow loop for `n = 5`:

| term `k` | sign | running sum |
|---|---|---|
| 1 | + | 1 |
| 2 | - | -1 |
| 3 | + | 2 |
| 4 | - | -2 |
| 5 | + | 3 |

`n = 5` is odd, and the formula gives `(5 + 1) // 2 = 3`. They agree.

## Code

```python
n = int(input())
if n % 2 == 0:
    print(-(n // 2))
else:
    print((n + 1) // 2)
```

## Complexity

A fixed number of operations whatever `n` is: O(1). The loop version is O(n).

## Another way

Write a slow loop version first, run it for `n = 1` to `20`, and compare with your formula for every value.
This "brute force checker" is how competitive programmers test a clever formula before trusting it.
Keep the loop for checking only; submit the formula.

## Edge cases

- `n = 1`: odd, `(1 + 1) // 2 = 1`.
- `n = 10^18`: even, answer `-5 * 10^17`. With `/` instead of `//` you get a float and may print
  `-5e+17`, which is the wrong format (and for other large `n` the digits are wrong too).
