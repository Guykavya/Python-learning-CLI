## Approach

Plan the special cases first, then the main loop.

1. **Invalid base** (not 2..16): print `invalid base` and do nothing else. Do this first, because
   base 1 or 0 would break the loop.
2. **Zero**: print `0`. The loop below would print nothing for 0.
3. **Sign**: remember `"-"` if `n < 0`, and work with `m = abs(n)`. Python's `%` and `//` round
   toward minus infinity, so on negative numbers they do not give digits.
4. **Digits**: `m % b` is the last digit in base `b` and `m // b` removes it, exactly like `% 10`
   and `// 10` in base 10. The digits come out right to left, so each new character goes in front:
   `result = DIGITS[m % b] + result`.

## Trace

Input `n = -10`, `b = 3`:

| m (before) | m % 3 | digit char | result | m // 3 |
|---|---|---|---|---|
| 10 | 1 | `1` | `1` | 3 |
| 3 | 0 | `0` | `01` | 1 |
| 1 | 1 | `1` | `101` | 0 |

The loop stops at `m = 0`. Output: `-` + `101` = `-101`. Check: 1*9 + 0*3 + 1 = 10.

## Code

```python
n = int(input())
b = int(input())

DIGITS = "0123456789ABCDEF"

if b < 2 or b > 16:
    print("invalid base")
elif n == 0:
    print("0")
else:
    sign = ""
    if n < 0:
        sign = "-"
    m = abs(n)
    result = ""
    while m > 0:
        # m % b is the LAST digit, so put it in front of what we have.
        result = DIGITS[m % b] + result
        m //= b
    print(sign + result)
```

## Complexity

Each step divides `m` by `b`, so the loop runs once per output digit: about log base `b` of `|n|`
times, at most 60 for `10^18` in base 2. O(log n) time. Building the string by prepending copies it
each time, which is O(d^2) for `d` digits, but `d` is at most 60 so it does not matter.

## Another way

**Highest power first.** Find the largest power of `b` that is at most `m` (start at 1 and multiply
by `b` while `power * b <= m`). Then repeatedly take `m // power` as the next digit (left to right),
set `m %= power`, and divide `power` by `b`. This produces digits in reading order, so you can append
them. It is the method you would use to convert by hand on paper with a table of powers. The
remainder method is shorter and harder to get wrong, so prefer it.

## Edge cases

- `n = 0` in a valid base: `0`. With an invalid base: `invalid base` (the base is checked first).
- `b = 10`: the output equals the input, a good self-check.
- `-10^18`: the sign is handled separately; `abs()` makes the loop identical to the positive case.
