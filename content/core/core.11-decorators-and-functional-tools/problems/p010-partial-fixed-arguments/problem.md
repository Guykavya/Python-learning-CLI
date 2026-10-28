# functools.partial: fix some arguments

`partial(f, *some_args, **some_kwargs)` returns a new callable. When you call it, it calls `f` with the
fixed arguments **plus** the ones you give now.

In `solution.py`, `power(base, exp)` is already written. Using `functools.partial` (not `def` and not
`lambda`), create four module-level names:

| Name | Meaning | Example |
|---|---|---|
| `square` | `power` with `exp` fixed to 2 | `square(5)` → `25` |
| `cube` | `power` with `exp` fixed to 3 | `cube(2)` → `8` |
| `from_binary` | `int` with `base` fixed to 2 | `from_binary("1010")` → `10` |
| `from_hex` | `int` with `base` fixed to 16 | `from_hex("ff")` → `255` |

**Examples**

```python
square(5)            # 25
cube(2)              # 8
from_binary("111")   # 7
from_hex("1A")       # 26
square.func          # <function power ...>   (a partial object remembers its function)
square.keywords      # {'exp': 2}
```
