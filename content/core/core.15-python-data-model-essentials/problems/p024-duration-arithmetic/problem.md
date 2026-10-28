# A Duration type with arithmetic

Time spans need rules: they cannot be negative, adding two is a duration, but dividing two gives a plain
ratio. Build `Duration(seconds)` in `solution.py`:

- `Duration(seconds)` stores a non-negative `int`. Negative values raise `ValueError`.
- `Duration.of(hours=0, minutes=0, seconds=0)` is a class method that builds one from parts.
- `a + b`: a `Duration`. `a - b`: a `Duration`, but if the result would be negative raise `ValueError`.
- `d * n` and `n * d` for an `int` `n >= 0`: a `Duration`.
- `d // n` for an `int` `n > 0`: a `Duration` (whole seconds, rounded down).
- `a / b` for two `Duration`s: a `float` ratio (`ZeroDivisionError` if `b` is zero).
- `==`, `<`, `<=`, `>`, `>=` between durations, and `hash` consistent with `==`.
- `str(d)` is `H:MM:SS` where hours may exceed 24 (`"25:00:00"`); `repr(d)` is `Duration(3723)`.
- Every other operand type: `TypeError`.

**Example**

```python
a = Duration.of(hours=1, minutes=2, seconds=3)
print(a)                      # 1:02:03
print(repr(a))                # Duration(3723)
print(a + Duration(57))       # 1:03:00
print(a * 2)                  # 2:04:06
print(Duration(90) / Duration(60))   # 1.5
print(Duration(10) - Duration(20))   # ValueError
```
