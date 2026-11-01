## Hint 1

For each `print` line, first list every dotted lookup **on `t`** that happens while its
arguments are evaluated, including lookups made inside a property or a method that runs.
Each one prints `get NAME`. Then ask for each lookup: did the normal lookup succeed (instance
dict, class, property returned) or raise `AttributeError`? Only a failure prints `fallback NAME`.

For `E` and `F`: does `len(t)` go through `t.__len__` written with a dot, or straight to the type?

## Hint 2

```
t.NAME:
    print "get NAME"
    try normal lookup (data descriptor / instance dict / class attribute / property getter)
    if it raised AttributeError:
        print "fallback NAME"
        if NAME starts with "_": raise AttributeError   -> hasattr gives False, getattr gives the default
        else: return "<NAME>"

len(t)  -> type(t).__len__(t)       no "get __len__", but the body does self.size
repr(t) -> type(t).__repr__(t)      nothing printed by the hooks
type(t) -> not an attribute lookup on t
```

In `C`, `self.width` does not exist, so it becomes the string `"<width>"`, and a string times 2 repeats it.
