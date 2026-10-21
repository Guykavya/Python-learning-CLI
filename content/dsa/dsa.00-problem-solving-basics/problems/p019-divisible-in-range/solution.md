## Approach

Check every integer from `a` to `b`. `range(a, b + 1)` is needed because `range` never includes its stop value.
A number `x` is divisible by `k` exactly when `x % k == 0`. In Python this also works for negatives:
`-6 % 3` is `0`, while `-5 % 3` is `1` (not 0), so negative multiples are found correctly.

## Trace

Input `-6`, `6`, `3`, one row per round of the loop:

| x | x % 3 | divisible? | count after |
|---|---|---|---|
| -6 | 0 | yes | 1 |
| -5 | 1 | no | 1 |
| -4 | 2 | no | 1 |
| -3 | 0 | yes | 2 |
| -2 | 1 | no | 2 |
| -1 | 2 | no | 2 |
| 0 | 0 | yes | 3 |
| 1 | 1 | no | 3 |
| 2 | 2 | no | 3 |
| 3 | 0 | yes | 4 |
| 4 | 1 | no | 4 |
| 5 | 2 | no | 4 |
| 6 | 0 | yes | 5 |

Printed: `5`.

## Code

```python
a = int(input())
b = int(input())
k = int(input())

count = 0
for x in range(a, b + 1):
    if x % k == 0:
        count += 1

print(count)
```

## Complexity

The loop visits `b - a + 1` numbers, so O(b - a) time and O(1) extra space. With at most about two million numbers this is fast enough.

## Another way

**A formula with no loop.** The number of multiples of `k` from 1 up to `n` is `n // k`. Using Python's floor
division (which rounds down, also for negatives), the count of multiples of `k` in `[a, b]` is

```python
print(b // k - (a - 1) // k)
```

For `-6, 6, 3`: `6 // 3 = 2` and `-7 // 3 = -3`, so `2 - (-3) = 5`. This is O(1) and works even when the range
is billions wide, where the loop would be far too slow. Prefer it whenever the range can be huge. The loop is
easier to trust, and is a good way to check the formula on small inputs.

## Edge cases

- `a == b`: the range has one number; the answer is 1 or 0.
- `k = 1`: every number counts, answer `b - a + 1`.
- `k` bigger than the whole range: the answer may be 0 or 1 (1 only if a multiple, such as 0, lies inside).
