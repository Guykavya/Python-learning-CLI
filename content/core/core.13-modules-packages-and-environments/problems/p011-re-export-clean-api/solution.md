## Approach

Put each function where it belongs (`length.py`, `temperature.py`), put the shared helper in a private
module (`_rounding.py`), and let `__init__.py` be the **front desk**: it imports the public names from the
submodules, lists them in `__all__`, and holds `__version__`. Users then depend only on
`unitkit.to_miles`; you can later move `to_miles` to another file and only `__init__.py` changes.

All imports inside the package are **relative** (`from ._rounding import r2`). The dot means "my own
package", whatever its name is. An absolute `from unitkit._rounding import r2` breaks when the folder is
renamed (or copied into another project), and `from _rounding import r2` only works when the `unitkit`
folder itself happens to be on `sys.path`.

## Code

```python
from pathlib import Path

INIT = '''"""unitkit: small unit conversions."""
from .length import to_km, to_miles
from .temperature import to_celsius, to_fahrenheit

__all__ = ["to_miles", "to_km", "to_fahrenheit", "to_celsius"]
__version__ = "1.0.0"
'''

ROUNDING = '''def r2(x):
    return round(x, 2)
'''

LENGTH = '''from ._rounding import r2


def to_miles(km):
    return r2(km * 0.621371)


def to_km(miles):
    return r2(miles * 1.609344)
'''

TEMPERATURE = '''from ._rounding import r2


def to_fahrenheit(c):
    return r2(c * 9 / 5 + 32)


def to_celsius(f):
    return r2((f - 32) * 5 / 9)
'''

FILES = {
    "__init__.py": INIT,
    "_rounding.py": ROUNDING,
    "length.py": LENGTH,
    "temperature.py": TEMPERATURE,
}


def write_unitkit(root):
    pkg = Path(root) / "unitkit"
    pkg.mkdir(parents=True, exist_ok=True)
    for name, text in FILES.items():
        (pkg / name).write_text(text, encoding="utf-8")
```

## Complexity

Writing is O(size of the sources). Each conversion is O(1).

## Another way

The `write_package` helper from p010 can write the `FILES` dict for you. In a real project you would keep
the package as normal files in `src/unitkit/` and install it with `pip install -e .` instead of
generating it from strings. The `_` prefix is only a convention: Python does not stop anyone from
importing `unitkit._rounding`, but it tells them they do so at their own risk.
