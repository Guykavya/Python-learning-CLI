# Guard decorators: @typed and @in_range

A marks system keeps getting bad input: text instead of numbers, and marks like 150. Instead of writing the
same checks at the top of every function, write two decorator factories that do the checking.

Write in `solution.py`:

### `typed(*types)`

Checks the **positional** arguments of each call before the function runs. Keyword arguments are passed on
without a check.

- If the number of positional arguments is not `len(types)`, raise
  `TypeError(f"{name}() expects {len(types)} positional arguments, got {count}")`.
- Argument number `i` (counting from 1) must pass `isinstance(arg, types[i - 1])`. If not, raise
  `TypeError(f"{name}() argument {i} must be {wanted}, got {actual}")`, where `wanted` and `actual` are type
  names such as `int` and `str` (use `.__name__`).

### `in_range(low, high)`

Every positional argument that is an `int` or a `float` must satisfy `low <= x <= high`. Other values are
ignored. If one is outside, raise `ValueError(f"{name}() argument {i} = {x} is outside {low}..{high}")`.

### Both

- `name` is the decorated function's name.
- Use `functools.wraps`, so the name stays correct when the decorators are **stacked**.
- If all checks pass, call the function and return its result.

**Example**

```python
@typed(int, int)
@in_range(0, 100)
def add_marks(a, b):
    return a + b

add_marks(40, 35)      # 75
add_marks("40", 35)    # TypeError: add_marks() argument 1 must be int, got str
add_marks(40)          # TypeError: add_marks() expects 2 positional arguments, got 1
add_marks(40, 150)     # ValueError: add_marks() argument 2 = 150 is outside 0..100
```
