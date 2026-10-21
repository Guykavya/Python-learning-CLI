## Hint 1

What does a caller learn from a function that prints "too short" and returns? What do they learn
from one that raises `ValueError`?

## Hint 2

Which built-in tells you whether a value is a `str`? (Chapter section 9 uses it.) Do the type
check first: `len(42)` would raise its own, less helpful, `TypeError`.

## Hint 3

```
if not isinstance(name, str): raise TypeError(f"... got {type(name).__name__}")
if not 3 <= len(name) <= 15: raise ValueError(f"... got {len(name)}")
for ch in name:
    if not (ch.isalnum() or ch == "_"): raise ValueError(f"... found {ch!r}")
if name[0].isdigit(): raise ValueError("...")
return name
```
