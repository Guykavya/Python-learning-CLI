## Approach

`importlib.import_module(name)` is the function form of `import`: it takes a string and returns the
module. The tricky part is deciding **which** `ModuleNotFoundError` means "not installed". The error's
`.name` tells us the module Python could not find. If it is the module we asked for, or a parent package
of it, the module does not exist and we return the default. If it is some other name, our module exists
but has a broken import, and we must not hide that.

For the parent test, `name.startswith(e.name + ".")` is right, and `name.startswith(e.name)` is wrong:
`"broken".startswith("bro")` is `True`, but `bro` is not a parent of `broken`.

## Code

```python
import importlib


def import_or_default(name, default=None):
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError as e:
        if e.name == name or name.startswith(f"{e.name}."):
            return default
        raise
```

## Complexity

The first call costs one real import (searching `sys.path`, running the module). Later calls are a
dictionary lookup in `sys.modules`.

## Another way

`importlib.util.find_spec(name)` returns `None` when a top-level module cannot be found, without running
it. You can check that first and only then import. The `try` version is simpler and is what the
"optional dependency" pattern in real projects looks like:

```python
try:
    import ujson as json
except ModuleNotFoundError:
    import json
```
