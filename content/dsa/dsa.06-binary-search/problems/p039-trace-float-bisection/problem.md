# Trace a bisection on real numbers

Predict **exactly** what this program prints. Do not run it.

```python
lo, hi = 1.0, 2.0
for i in range(6):
    mid = (lo + hi) / 2
    if mid * mid < 2:
        lo = mid
    else:
        hi = mid
    print(i + 1, lo, hi, hi - lo)
print("estimate", (lo + hi) / 2)
print("true value", 2 ** 0.5)
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

We look for the square root of 2 by halving the interval `[1.0, 2.0]` six times. The condition `mid * mid < 2` is True while `mid` is still below the root.
All numbers that appear are sums of powers of two (1.5, 1.25, 1.375, ...), so Python prints them exactly. The last two lines compare the estimate with the true value: the second is a float that Python prints with 16 digits.
Each loop line shows the step number, `lo`, `hi` and the width `hi - lo`.

## After you answer

1. By what factor does the width shrink at every step? How wide is the interval after 20 steps?
2. Why does this loop use `lo = mid` and `hi = mid`, while the integer templates use `mid + 1`?
3. Why is a fixed number of steps safer than `while hi - lo > eps` for tiny `eps`?
