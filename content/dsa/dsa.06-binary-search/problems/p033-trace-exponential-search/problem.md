# Trace a doubling search

Predict **exactly** what this program prints. Do not run it.

```python
def f(i):
    return i * i


target = 500
bound = 1
while f(bound) < target:
    print("double: f(", bound, ") =", f(bound))
    bound *= 2
print("bound", bound)
lo, hi = bound // 2, bound
while lo < hi:
    mid = (lo + hi) // 2
    ok = f(mid) >= target
    print("lo", lo, "hi", hi, "mid", mid, "f(mid)", f(mid), "ok", ok)
    if ok:
        hi = mid
    else:
        lo = mid + 1
print("answer", lo)
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

The function `f(i) = i * i` is increasing, and we look for the first `i` with `f(i) >= 500`. We do not know how large `i` can be, so the first loop doubles `bound` until `f(bound) >= 500`.
Then a half-open binary search runs on `[bound // 2, bound)`... with `hi = bound` itself as a possible answer. Check each printed number by calculating `f` yourself.
Spaces: `print` puts one space between its arguments, so `"f(", bound, ") ="` prints as `f( 1 ) = 1`.

## After you answer

1. How many `f` evaluations did the doubling phase use? How many the binary phase? Compare with a linear scan from 1.
2. Why is it safe to start the second phase at `bound // 2`?
3. If the target were 5 * 10^17, about how many doublings would be needed?
