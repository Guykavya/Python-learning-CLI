# Safe division

Write `safe_divide(a, b)` that returns `a / b`, or `None` when `b` is zero.

- Use `try`/`except ZeroDivisionError` around the division. Do not test `b == 0` first:
  this problem practises the EAFP style from section 14.
- Zero can be the int `0` or the float `0.0`; both raise `ZeroDivisionError`.
- If `a` or `b` is not a number (for example the string `"6"`), the division raises
  `TypeError`. That is the caller's bug: let it propagate.

**Examples**

```python
safe_divide(6, 3)       # 2.0
safe_divide(1, 0)       # None
safe_divide(0, 5)       # 0.0
safe_divide(-3, 0.0)    # None
safe_divide("6", 2)     # raises TypeError
```
