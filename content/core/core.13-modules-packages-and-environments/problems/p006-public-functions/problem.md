# List a module's own public functions

`dir(module)` lists every name in a module: functions, constants, imported modules, imported functions,
and "private" helpers that start with `_`. Often you only want the functions the module itself defines
for others to use.

Write `public_functions(module)` in `solution.py`. It returns a **sorted list** of the names in `module`
that:

1. do **not** start with `_`,
2. are callable (`callable(value)` is `True`), and
3. were **defined in this module**, not imported. Every function remembers where it was defined in its
   `__module__` attribute; compare that with `module.__name__`. Some values have no `__module__`
   attribute (a module object, for example), so use `getattr(value, "__module__", None)`.

**Example**

```python
# shapes.py
from math import pi, sqrt
import json

RATE = 2
_cache = {}


def area(r):
    return pi * r * r


def _helper():
    return 1


def side_from_area(a):
    return sqrt(a)


double = lambda x: x * RATE
```

```python
import shapes
print(public_functions(shapes))   # ['area', 'double', 'side_from_area']
```

`sqrt` is callable but its `__module__` is `math`. `json` is a module, not a function. `RATE` is not
callable. `_helper` is private.
