- Returning every name from `dir()`. It includes `__name__`, `__file__`, imported modules and constants.
- Checking only `callable`. Imported functions (`sqrt`, `print`) are callable too.
- Writing `value.__module__` directly. A module object such as `json` has no `__module__`, so it raises
  `AttributeError`. Use `getattr` with a default.
- Comparing `__module__` with the file name (`"shapes.py"`). It is the module name, `"shapes"`.
