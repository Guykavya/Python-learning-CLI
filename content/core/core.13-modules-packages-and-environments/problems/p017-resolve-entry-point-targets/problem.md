# Resolve "module:function" targets like entry points

In a `pyproject.toml` you write lines like

```toml
[project.scripts]
notes = "notes_app.cli:main"
```

When you install the package, pip makes a `notes` command that imports `notes_app.cli` and calls its
`main`. The string `"notes_app.cli:main"` is called an **object reference**: a module path, a colon,
then an attribute path. Many tools use the same format (gunicorn's `app:server`, pytest plugins,
task runners).

Write two functions in `solution.py`.

### `resolve(target)`

- `target` has the form `"module.path:attr.path"`.
- The text before the colon is the module to import with `importlib.import_module`.
- The text after the colon is one name or several names joined by dots. Follow them one by one with
  `getattr`. `"os.path:join"` gives `os.path.join`. `"toolbox:text.shout"` imports `toolbox`, then
  takes `toolbox.text`, then `.shout`.
- Raise `ValueError` if the target is malformed: not exactly one colon, an empty module part or an
  empty attribute part, or an empty name between dots (like `"a..b:f"` or `"a:f."`).
- If the module cannot be imported, let the import error (for example `ModuleNotFoundError`) go up
  unchanged. Do not hide it.
- If an attribute is missing, raise `AttributeError` with a message that contains the full target
  string, so the user knows which line of their config is wrong.

### `dispatch(table, command, args)`

`table` maps command names to target strings. Find the target for `command`, resolve it and call it
with the list `args`. Return what it returns.

- An unknown command raises `KeyError`.
- If the resolved object is not callable, raise `TypeError`.

## Example

```python
>>> import os
>>> resolve("os.path:join") is os.path.join
True
>>> resolve("json:dumps")([1, 2])
'[1, 2]'
>>> resolve("json")
Traceback (most recent call last):
ValueError: target must look like 'module:attribute', got 'json'
>>> table = {"dump": "json:dumps", "sep": "os:sep"}
>>> dispatch(table, "dump", ["a"])
'["a"]'
>>> dispatch(table, "sep", [])
Traceback (most recent call last):
TypeError: 'os:sep' is not callable
```

The exact wording of the messages is up to you, except that the `AttributeError` must contain the
target.
