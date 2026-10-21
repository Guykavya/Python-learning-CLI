# Positional-only and keyword-only power

Write `power(base, exp, /, *, modulo=None)` that returns `base ** exp`, or, if `modulo` is
given, `(base ** exp) % modulo`.

The signature itself is part of the exercise:

- `base` and `exp` must be **positional-only**: `power(base=2, exp=3)` must raise `TypeError`.
- `modulo` must be **keyword-only**: `power(2, 3, 5)` must raise `TypeError`.

Python raises those errors for you once the `/` and `*` are in the right places.

**Examples**

```python
power(2, 10)              # 1024
power(2, 10, modulo=1000) # 24
power(5, 0)               # 1
power(7, 2, modulo=7)     # 0
```

For huge exponents with a modulo, the built-in `pow(base, exp, modulo)` is far faster than
computing `base ** exp` first; you may use it.
