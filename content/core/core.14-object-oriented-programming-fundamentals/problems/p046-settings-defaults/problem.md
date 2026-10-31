# Settings with class-level defaults

An app has settings like `port` and `debug`. Most runs use the defaults; a few values change per
run; and a production setup has different defaults. Python's attribute lookup gives this almost for
free: **defaults are class attributes**, an override is an **instance attribute** that hides the
class value, and a subclass can change defaults. Write it in `solution.py`.

**`Settings`** has these class attributes (the defaults):

```python
debug = False
host = "localhost"
port = 8000
workers = 1
```

A **setting** is any class attribute (also inherited ones) whose name does not start with `_` and
whose value is not callable (so methods are not settings).

- `Settings.names()` (classmethod): the sorted list of setting names of the class it is called on.
  `dir(cls)` lists all attribute names, inherited ones included; `callable(x)` tells you if `x` is
  a function or method.
- `Settings(**overrides)`: for each keyword, the name must be a setting of **this** class, otherwise
  `TypeError` with a message containing `unknown setting`. The value must have **exactly** the same
  type as the default (`type(value) is type(default)`), otherwise `TypeError`. (So `port=True` and
  `debug=1` are refused.) Store **only** the given overrides on the object. Settings that were not
  given must **not** be copied onto the object: reading them falls through to the class.
- `as_dict()`: a dict of every setting name (sorted) to its current value for this object.
- `overrides()`: a dict of only the values stored on this object.
- `reset(name)`: remove this object's override for `name`, so the default shows again. If there is
  no override, do nothing. An unknown name raises `TypeError`.
- `with_changes(**changes)`: return a **new** object of the **same class**, with this object's
  overrides plus `changes`.

**Two subclasses**

- `DevSettings(Settings)`: `debug = True`.
- `ProductionSettings(Settings)`: `host = "0.0.0.0"`, `port = 80`, `workers = 4`.

**Example**

```python
s = Settings(port=9000)
s.port, s.host                  # (9000, 'localhost')
s.overrides()                   # {'port': 9000}
p = ProductionSettings(workers=8)
p.as_dict()     # {'debug': False, 'host': '0.0.0.0', 'port': 80, 'workers': 8}
p2 = p.with_changes(debug=True)
type(p2).__name__, p2.overrides()   # ('ProductionSettings', {'workers': 8, 'debug': True})
s.reset("port")
s.port                          # 8000
Settings(colour="red")          # TypeError: unknown setting 'colour'
Settings(port="80")             # TypeError: port must be int, got str
```
