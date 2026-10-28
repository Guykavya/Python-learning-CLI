## Approach

Validate the string first, so a typo never triggers an import. Then use the two tools that match the
two halves: `importlib.import_module("a.b.c")` imports a dotted module (and its parent packages) and
returns it, and `getattr` follows attribute names one by one. Wrap only the `getattr` part to add the
target to the error message; import errors stay as they are, because their own message is the most
useful one.

## Code

```python
import importlib


def resolve(target):
    if target.count(":") != 1:
        raise ValueError(f"target must look like 'module:attribute', got {target!r}")
    module_name, attr_path = target.split(":")
    parts = attr_path.split(".")
    if not module_name or "" in module_name.split(".") or "" in parts:
        raise ValueError(f"empty name in target {target!r}")
    obj = importlib.import_module(module_name)
    for name in parts:
        try:
            obj = getattr(obj, name)
        except AttributeError:
            raise AttributeError(f"{target!r}: no attribute {name!r}") from None
    return obj


def dispatch(table, command, args):
    target = table[command]
    func = resolve(target)
    if not callable(func):
        raise TypeError(f"{target!r} is not callable")
    return func(args)
```

## Complexity

O(k) `getattr` calls for k names after the colon, plus the import (which is cached after the first time).

## Another way

The standard library already parses this format: `importlib.metadata.EntryPoint(name="x",
value="json:dumps", group="g").load()` imports and follows the path, exactly like `resolve`. It is good
to know it exists; writing it yourself shows that an entry point is nothing more than
`import_module` + `getattr`.

`from None` hides the original `AttributeError` in the traceback. Use `from e` (after
`except AttributeError as e:`) if you prefer to keep it.
