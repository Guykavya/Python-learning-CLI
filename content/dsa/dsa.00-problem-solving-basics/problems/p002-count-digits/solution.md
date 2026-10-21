## Approach

Each `n // 10` removes exactly one digit from the right. So the number of digits is the number of
times you can divide by 10 before reaching 0.

Two traps:

- Negative numbers. Take `abs(n)` first. The minus sign is not a digit.
- Zero. A `while n > 0` loop never runs for `0`, so the count would stay 0. But `0` has one digit.
  The reference handles this with a separate check before the loop.

## Trace

Input `-450`, so `n` becomes `450` after `abs()`.

| Iteration | `n` before | `n // 10` | `count` after |
|---|---|---|---|
| 1 | 450 | 45 | 1 |
| 2 | 45 | 4 | 2 |
| 3 | 4 | 0 | 3 |

The loop stops because `n` is 0. Output: `3`.

## Code

```python
n = abs(int(input()))
if n == 0:
    count = 1
else:
    count = 0
    while n > 0:
        n //= 10
        count += 1
print(count)
```

## Complexity

The loop runs once per digit. For a number with d digits that is O(d) steps, which is about O(log10 n).
Even a 50-digit number needs only 50 steps.

## Another way

Start `count` at 1 and divide first, then check:

```python
n = abs(int(input()))
count = 1
while n >= 10:
    n //= 10
    count += 1
print(count)
```

This version needs no special case for `0`, because it already counts the last digit before the loop.
Prefer it when you want fewer branches. The first version is easier to reason about when you are new,
because the special case is written out clearly.

Outside this exercise, `len(str(abs(n)))` is the quick way, and it is fine in real code.

## Edge cases

- `0` prints `1`, not `0`.
- `-7` prints `1`.
- `10`, `100`, `1000` check that trailing zeros are counted.
