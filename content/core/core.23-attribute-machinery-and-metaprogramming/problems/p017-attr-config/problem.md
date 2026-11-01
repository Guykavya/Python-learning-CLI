# Config with dotted access

Settings often arrive as nested dictionaries (from JSON, TOML or YAML). Typing
`config["database"]["host"]` everywhere is noisy; `config.database.host` reads better and
is what many libraries offer. `__getattr__` makes it a small class.

Copy `starter.py` to `solution.py` and write `Config(data)`, where `data` is a dict:

1. `cfg.name` returns `data["name"]`. If that value is itself a dict, return it wrapped in a
   `Config`, so `cfg.db.host` works at any depth. Other values (numbers, strings, lists) come
   back unchanged.
2. A missing key raises **`AttributeError`**, never `KeyError`. The message contains the
   **full dotted path**, for example `no config key 'db.prt'` for `cfg.db.prt`. (You may give
   `Config` an optional second parameter that remembers the path of a nested `Config`.) With
   `AttributeError`, `hasattr(cfg, "x")` and `getattr(cfg, "x", default)` work.
3. `dir(cfg)` lists the keys (so tab completion in the REPL shows them) **and** the normal
   attributes such as `to_dict`. Write `__dir__` for this.
4. `cfg.to_dict()` returns a plain dict equal to the data, as a **deep** copy: changing the
   returned dict (even a nested part of it) must not change `cfg`.
5. A key with the same name as a method, such as `"to_dict"`, does not break the method:
   `__getattr__` is only the fallback, and the method is found first. Such a key is still
   part of `to_dict()`; it just cannot be read as an attribute.

**Example**

```python
cfg = Config({"debug": True, "db": {"host": "localhost", "port": 5432}, "ports": [80, 443]})
cfg.debug              # True
cfg.db.host            # 'localhost'
cfg.ports              # [80, 443]
cfg.db.prt             # AttributeError: no config key 'db.prt'
hasattr(cfg, "cache")  # False
"host" in dir(cfg.db)  # True
d = cfg.to_dict()
d["db"]["host"] = "x"
cfg.db.host            # still 'localhost'
```
