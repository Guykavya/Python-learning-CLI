## Hint 1

Write the four files as four strings first, and test them by hand in a scratch folder. Which file does
`import unitkit` run? What must that file do so that `unitkit.to_miles` exists?

## Hint 2

Inside the package, `from .length import to_miles` means "the `length` module next to me". An absolute
`from unitkit.length import to_miles` also works, until the folder is renamed. Why? And why would
`from _rounding import r2` fail when the package is imported from outside its folder?

## Hint 3

```
INIT = '''from .length import to_miles, to_km
from .temperature import to_fahrenheit, to_celsius

__all__ = ["to_miles", "to_km", "to_fahrenheit", "to_celsius"]
__version__ = "1.0.0"
'''
ROUNDING = def r2(x): return round(x, 2)
LENGTH = from ._rounding import r2; to_miles → r2(km * 0.621371); to_km → r2(miles * 1.609344)
TEMPERATURE = from ._rounding import r2; to_fahrenheit, to_celsius the same way

pkg = Path(root) / "unitkit"; pkg.mkdir(exist_ok=True)
write each string to its file with encoding="utf-8"
```
