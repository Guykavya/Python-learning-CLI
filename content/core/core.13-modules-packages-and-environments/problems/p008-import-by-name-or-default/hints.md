## Hint 1

Wrap the `import_module` call in `try`/`except ModuleNotFoundError as e`. Print `e.name` for
`"no_such_lib"`, for `"no_such_lib.sub"` and for `"broken"`. Which ones are "the thing I asked for is missing"?

## Hint 2

```
try:
    return importlib.import_module(name)
except ModuleNotFoundError as e:
    if e.name == name or name.startswith(e.name + "."):
        return default
    raise
```

A bare `raise` inside `except` re-raises the same error with its traceback.
