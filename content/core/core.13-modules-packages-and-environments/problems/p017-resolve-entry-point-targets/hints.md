## Hint 1

Split the job in two halves: the part before the colon is a *module* (only `import` can give you
that), the part after it is a chain of *attributes* (only `getattr` can follow that). Which checks can
you do on the string alone, before you import anything?

## Hint 2

```text
if target.count(":") != 1: raise ValueError
module_name, attr_path = target.split(":")
parts = attr_path.split(".")
if module_name is empty, or "" in module_name.split("."), or "" in parts: raise ValueError
obj = importlib.import_module(module_name)      # errors go up by themselves
for name in parts:
    try: obj = getattr(obj, name)
    except AttributeError: raise AttributeError(f"{target!r}: no attribute {name!r}")
return obj
```

`dispatch`: `target = table[command]` (that already raises `KeyError`), resolve, check
`callable`, call with `args`.
