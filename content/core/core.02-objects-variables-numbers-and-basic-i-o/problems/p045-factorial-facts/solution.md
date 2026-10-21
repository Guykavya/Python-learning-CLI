## Approach

Python can compute `3000!` exactly (it has 9131 digits), but turning it into text is limited
to 4300 digits by default as a protection against very slow conversions. So we answer both
questions with arithmetic instead.

## Code

```python
import math

n = int(input())
f = math.factorial(n)
print("Digits:", int(math.log10(f)) + 1)
print("Trailing zeros:", n // 5 + n // 25 + n // 125 + n // 625)
```

## Why it works

- Digits: if `x` has `d` digits then `10**(d-1) <= x < 10**d`, so `d - 1 <= log10(x) < d`.
  Taking the floor gives `d - 1`. `math.log10` handles big ints specially, so it does not overflow.
- Zeros: `n // 5` counts multiples of 5, `n // 25` adds one more for each multiple of 25, and so on.
  This is called Legendre's formula.

## A caution

`math.log10` returns a float. If `x` were extremely close to a power of 10, the float could land on
the wrong side. A factorial larger than 1 is never a power of 10, and the tests check every case.
In core.04 you will learn a loop that divides by 10 and counts, which is exact.
