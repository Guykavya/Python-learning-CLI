## Approach

Every `p.name` read calls `Probe.__getattribute__`, which prints and then delegates to the normal
lookup (`object.__getattribute__` through `super()`). If that raises `AttributeError`, Python
calls `__getattr__`, which prints and returns a string instead of failing.

| Code | What happens | Printed |
|---|---|---|
| `Probe()` | `self.x = 1` is a write: no hook | nothing |
| `p.x` | found in the instance dict | `getattribute x`, `1` |
| `p.kind` | found on the class | `getattribute kind`, `probe` |
| `p.area` | property found on the class, returns 10 | `getattribute area`, `10` |
| `p.missing` | normal lookup fails, fallback runs | `getattribute missing`, `getattr missing`, `fallback-missing` |
| `p.broken` | the property raises `AttributeError`; to Python that looks exactly like "not found", so `__getattr__` runs | `getattribute broken`, `getattr broken`, `fallback-broken` |
| `getattr(p, "y", 0)` | `getattr` reads `p.y`; the fallback returns a value, so no `AttributeError` escapes and the default `0` is never used | `getattribute y`, `getattr y`, `fallback-y` |
| `hasattr(p, "z")` | reading works (fallback), so `True` | `getattribute z`, `getattr z`, `True` |
| `p.y = 5` | a write: no hook | nothing |
| `p.y` | now in the instance dict | `getattribute y`, `5` |
| `len(vars(p))` | `vars` reads the `__dict__` attribute, which goes through `__getattribute__`; the dict holds `x` and `y` | `getattribute __dict__`, `2` |

## Full output

```
getattribute x
1
getattribute kind
probe
getattribute area
10
getattribute missing
getattr missing
fallback-missing
getattribute broken
getattr broken
fallback-broken
getattribute y
getattr y
fallback-y
getattribute z
getattr z
True
getattribute y
5
getattribute __dict__
2
```

## Complexity

One extra function call per attribute read for `__getattribute__`; this is why defining it slows
every access on the class.

## Another way

Remove `__getattr__` and run the program again (in a `try` block for each line): `p.missing`,
`p.broken` and `getattr(p, "y", 0)` then behave normally (error, error, `0`). The `broken` case
is a real trap: a typo inside a property raises `AttributeError`, and a `__getattr__` hides it.
