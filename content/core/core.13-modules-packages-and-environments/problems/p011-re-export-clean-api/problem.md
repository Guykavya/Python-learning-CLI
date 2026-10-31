# A package with a clean public API

Users of a package should not need to know which file a function lives in. They should write
`import unitkit` and then `unitkit.to_miles(...)`. The package's `__init__.py` makes that possible by
**re-exporting** the public functions from its submodules. Helpers that are only for the package itself
go in a module whose name starts with `_`, which says "private, do not import this from outside".

Write `write_unitkit(root)` in `solution.py`. It creates this package inside the existing folder `root`
and returns nothing:

```text
root/
└── unitkit/
    ├── __init__.py
    ├── _rounding.py
    ├── length.py
    └── temperature.py
```

What each file must contain:

- **`_rounding.py`**: `r2(x)` returns `round(x, 2)`.
- **`length.py`**: `to_miles(km)` returns `km * 0.621371` and `to_km(miles)` returns `miles * 1.609344`,
  both rounded with `r2`.
- **`temperature.py`**: `to_fahrenheit(c)` returns `c * 9 / 5 + 32` and `to_celsius(f)` returns
  `(f - 32) * 5 / 9`, both rounded with `r2`.
- Both `length.py` and `temperature.py` get `r2` with a **relative import**: `from ._rounding import r2`.
- **`__init__.py`**: re-exports the four functions with relative imports, sets
  `__all__ = ["to_miles", "to_km", "to_fahrenheit", "to_celsius"]`, and sets `__version__ = "1.0.0"`.
  `r2` is **not** part of the package-level API.

Rules: importing the package prints nothing. Use relative imports inside the package, so it still works
when someone renames the folder.

**Example**

```python
write_unitkit("work")
# with "work" on sys.path:
import unitkit
unitkit.to_miles(10)           # 6.21
unitkit.to_fahrenheit(37)      # 98.6
unitkit.length.to_km(10)       # 16.09   (the submodule is reachable too)
unitkit.__version__            # '1.0.0'
hasattr(unitkit, "r2")         # False
from unitkit import *          # brings in exactly the four functions
```

Hint for writing source code into a string: a triple-quoted string keeps the line breaks.
