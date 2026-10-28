- Copying the function code into `__init__.py`. Then there are two `to_miles` functions that can drift
  apart. Import it instead, so `unitkit.to_miles is unitkit.length.to_miles`.
- `from _rounding import r2` inside `length.py`. It works only when you run from inside the folder, and
  fails as soon as the package is imported from outside.
- Absolute imports with the package name. They work until the folder is renamed.
- Importing `r2` in `__init__.py` "to be helpful". Everything at package level becomes API that users
  rely on and you must keep forever.
- Writing a separate `r2` in each module. One shared helper means one place to fix.
- Leaving a test `print(...)` in a module. Every import prints it.
