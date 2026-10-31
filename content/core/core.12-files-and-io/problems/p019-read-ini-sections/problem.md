# Read an INI file with configparser

An INI file has `[sections]` with `key = value` lines. Write two functions in `solution.py`:

- `read_ini(path)` returns a dict of dicts: `{section: {key: value}}`. All values are strings.
  A missing file gives `{}`.
- `get_int(path, section, option, fallback)` returns the option as an `int`.
  If the file, the section or the option is missing, return `fallback`.

**Example**

```ini
[server]
Port = 8080
host = example.org

[user]
name = Ravi
```

```python
read_ini("app.ini")
# {'server': {'port': '8080', 'host': 'example.org'}, 'user': {'name': 'Ravi'}}
get_int("app.ini", "server", "port", 80)   # 8080
get_int("app.ini", "server", "timeout", 30)   # 30
```
Note: `configparser` makes the keys lower case.
