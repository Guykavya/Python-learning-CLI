# Read a TOML config with defaults

Write `load_config(path)` in `solution.py`. Settings come from a TOML file. The defaults are:

```python
DEFAULTS = {"host": "localhost", "port": 8000, "debug": False, "tags": []}
```

- Read the TOML file with the standard `tomllib` module.
- Return a **new** dict: the defaults, with the values from the file on top. Keys in the file that are not
  in the defaults are kept.
- If the file does not exist, return a copy of the defaults.
- Each call must return fresh data: changing the returned dict (or its `tags` list) must never change the
  defaults for the next call.
- Broken TOML raises `tomllib.TOMLDecodeError`. Do not hide it.

**Example**

```toml
port = 9000
tags = ["a", "b"]
```

```python
load_config("app.toml")
# {'host': 'localhost', 'port': 9000, 'debug': False, 'tags': ['a', 'b']}
```
