# Settings with defaults via `__getattr__`

`__getattr__(self, name)` is the **fallback** hook: Python calls it only when the normal lookup
(instance dict, class) did not find `name`. That makes it perfect for "use the stored value if
there is one, else a default".

Copy `starter.py` to `solution.py` and write the class `Settings(values, defaults=None)`:

- `values` and `defaults` are dicts (`defaults` may be left out).
- `s.name` returns `values[name]` if it was given, else `defaults[name]`.
- After `s.name = something`, reading `s.name` returns the new value.
- An unknown name raises **`AttributeError`** whose message contains the name, never `KeyError`.
  That is what makes `hasattr(s, name)` and `getattr(s, name, default)` work.
- Names that start with an underscore (`_cache`, `__deepcopy__`, `__setstate__` and so on) are
  **never** looked up in the defaults: if the normal lookup did not find them, raise
  `AttributeError` at once.

Why the last rule? `copy.copy`, `copy.deepcopy` and `pickle` create a new object **without
calling `__init__`** and then ask it for optional methods like `__setstate__`. On that empty
object, a `__getattr__` that reads `self._defaults` finds nothing, so Python calls
`__getattr__("_defaults")`, which reads `self._defaults` again... until `RecursionError`.

**Example**

```python
s = Settings({"host": "db.local"}, {"host": "localhost", "port": 5432})
s.host                    # 'db.local'   (from values)
s.port                    # 5432         (from defaults, via __getattr__)
s.timeout                 # AttributeError: 'Settings' object has no attribute 'timeout'
getattr(s, "timeout", 30) # 30
hasattr(s, "__deepcopy__")  # False
copy.deepcopy(s).port     # 5432
```
