## Hint 1

For every read `p.something` the first line is always `getattribute something`. Then ask: did
the normal lookup (instance dict, class, property) **succeed**, or did it raise
`AttributeError`? Only in the second case does a `getattr something` line follow.
What happens when a property's code itself raises `AttributeError`?

## Hint 2

```
p.x, p.kind, p.area  -> found normally            -> 1 line from the hook, then the value
p.missing            -> not found -> __getattr__   -> 2 hook lines, then "fallback-missing"
p.broken             -> property raises AttributeError -> looks "missing" -> __getattr__ runs
getattr(p, "y", 0)   -> the default is used only if AttributeError escapes; does it?
hasattr(p, "z")      -> True if reading p.z does not raise AttributeError
p.y = 5              -> a write: no hook prints
vars(p)              -> vars reads p.__dict__ ... which is an attribute read
```
