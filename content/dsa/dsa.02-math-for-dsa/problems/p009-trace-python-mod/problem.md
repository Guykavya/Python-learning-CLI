# Trace Python's `%` and `//` with negative numbers

In C, C++ and Java, `-17 % 5` is `-2`. In Python it is not. Python rounds division **down** (toward minus
infinity), and `%` always matches: `a == (a // b) * b + a % b`. Predict **exactly** what this program prints.
Do not run it.

```python
print(17 // 5, 17 % 5)
print(-17 // 5, -17 % 5)
print(17 // -5, 17 % -5)
print(-17 // -5, -17 % -5)
print(divmod(-17, 5))
print(int(-17 / 5))
print(-7 % 7, 0 % 7)
print((-3) % 10)
print(-3 % 10)
print(-(3 % 10))
print(-2 ** 2, (-2) ** 2)
a, b = 23, -4
q, r = divmod(a, b)
print(q, r, q * b + r == a)
print((7 - 10) % 12)
print(5 // 0.5, 7.5 % 2)
```

Write your answer in `answer.txt`, one line per printed line.

## Method

For each `a // b`, compute the exact quotient, then round **down**: -3.4 becomes -4, 3.4 becomes 3.
Then find `a % b` from `a - (a // b) * b`. The result of `%` has the **same sign as `b`** (or is 0).

## After you answer

Why does the identity `q * b + r == a` matter? Think of the clock: `(7 - 10) % 12` is 9 o'clock.
That is why modular code in Python never needs the C-style fix `(x % m + m) % m`.
