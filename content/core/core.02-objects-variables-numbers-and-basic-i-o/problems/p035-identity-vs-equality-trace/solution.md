## Walkthrough

| Line | Output | Why |
|---|---|---|
| `x is y` | `True` | `y = x` binds a second name to the same object |
| `x, y` | `300 301` | `y += 1` made a new int 301 and moved `y` to it; `x` still names 300 |
| `x is y` | `False` | the names now refer to different objects |
| `a == b, a is b` | `True True` | same object, so equal and identical |
| `a == c` | `True` | equal values, whatever their identity |
| `type(c) is float` | `True` | there is exactly one `float` type object, so `is` is the right test |
| `n is None, n == None` | `True True` | both work here, but `is None` is the correct style |
| `1 == 1.0` | `True` | numeric values compare equal across types |
| `type(1) is type(1.0)` | `False` | `int` and `float` are different types |
| `isinstance(True, int)` | `True` | `bool` is a subclass of `int` |
| `id(a) == id(b)` | `True` | `a is b` means exactly `id(a) == id(b)` |

## What was left out on purpose

`c is a` is not in this program. Whether two equal floats or ints made separately are the same
object depends on the Python implementation (CPython caches small ints from -5 to 256, for example).
Never write code that depends on it. Use `is` only for `None`, `True`/`False` and type checks.
