# Apply a function twice

Write `apply_twice(func, value)` that calls `func` on `value`, then calls `func` again on the
result, and returns that final result.

**Examples**

```python
def add_three(n):
    return n + 3

apply_twice(add_three, 10)      # 16
apply_twice(str.upper, "hi")    # "HI"
apply_twice(abs, -7)            # 7
```

`func` is passed **without** parentheses: you receive the function itself.
