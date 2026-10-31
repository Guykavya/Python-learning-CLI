# A plugin loader with importlib

Many tools (pytest, Flask, text editors) let you drop a `.py` file into a folder and the tool picks
it up as a **plugin**. The tool does not know the file names in advance, so it cannot write
`import hello`. It has to import the files *dynamically*.

Write two functions in `solution.py`.

### `load_plugins(folder)`

`folder` is a `str` or `Path`. Look at the `.py` files directly inside it (not in sub-folders), in
sorted order of their file names.

- Skip files whose name starts with `_` (like `_helpers.py` or `__init__.py`). They are private.
- Load every other file as a module.
- If loading the file raises an exception (any `Exception`, for example a `SyntaxError` or a
  `ZeroDivisionError` in its top-level code), do not crash: put the file's stem in a `failed` list.
- If the module has a **callable** attribute named `register`, add it to a dict:
  `stem -> register function`. A module without `register` (or where `register` is not callable,
  like `register = 5`) is ignored.

Return the tuple `(plugins, failed)`. The dict keys are in sorted order, and `failed` is sorted.
If `folder` does not exist, raise `FileNotFoundError`.

Rules:

- Load the files **fresh on every call**. If a plugin file changes between two calls, the second call
  must see the new code. (So the module cache of `import` is not what you want here.)
- Do not change `sys.path`.

### `run_plugins(folder, app)`

Load the plugins, then call each `register(app)` in sorted order. `app` is a dict that plugins may
change. Return the list of stems whose `register` was called.

### The tool for loading a file by path

`importlib.util` can load a module straight from a file path, without `sys.path` and without the
cache:

```python
import importlib.util

spec = importlib.util.spec_from_file_location("plugin_hello", "plugins/hello.py")
module = importlib.util.module_from_spec(spec)   # an empty module object
spec.loader.exec_module(module)                    # runs the file's code inside it
module.register                                    # now you can use its names
```

`exec_module` raises whatever the file's code raises.

## Example

```text
plugins/
├── _shared.py     (skipped: private)
├── broken.py      x = 1 / 0
├── greet.py       def register(app): app.setdefault("commands", []).append("greet")
├── notes.py       VALUE = 3            (no register)
└── upper.py       def register(app): app.setdefault("commands", []).append("upper")
```

```python
>>> plugins, failed = load_plugins("plugins")
>>> list(plugins)
['greet', 'upper']
>>> failed
['broken']
>>> app = {}
>>> run_plugins("plugins", app)
['greet', 'upper']
>>> app
{'commands': ['greet', 'upper']}
```
