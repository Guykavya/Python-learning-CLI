# Name the error family

Write `error_family(func, *args)` that calls `func(*args)` and reports which **family** of
exception it raised:

| What happened | Return |
|---|---|
| no exception | `"ok"` |
| any `LookupError` (`KeyError`, `IndexError`, ...) | `"lookup"` |
| any `ArithmeticError` (`ZeroDivisionError`, `OverflowError`, ...) | `"arithmetic"` |
| any `ValueError` (including its subclasses) | `"value"` |
| any `TypeError` | `"type"` |

Any other exception (for example `NameError`, or `KeyboardInterrupt`) must **propagate**
unchanged: do not catch it.

Use one `except` clause per family, naming the **parent** classes from chapter section 4. Do not
list every child class by hand.

**Examples**

```python
error_family(len, "abc")                 # 'ok'
error_family(lambda: {}["x"])            # 'lookup'
error_family(lambda: [1][3])             # 'lookup'
error_family(lambda: 2.0 ** 10000)       # 'arithmetic'   (OverflowError)
error_family(int, "x")                   # 'value'
error_family(len, 5)                     # 'type'
error_family(lambda: missing_name)       # raises NameError
```
