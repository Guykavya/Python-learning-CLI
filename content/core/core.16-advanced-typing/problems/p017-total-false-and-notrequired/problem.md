# Optional keys: `total=False` and `NotRequired`

Not every key of a dict is always there. A TypedDict has two ways to say "this key may be
missing":

```python
class Base(TypedDict):                 # both keys required
    host: str
    port: int

class Config(Base, total=False):       # ALL keys defined in this class are optional
    debug: bool

class Other(TypedDict):                # only this key is optional
    host: str
    debug: NotRequired[bool]
```

In `solution.py` write:

1. `Config`: required keys `host: str` and `port: int`; optional keys `debug: bool` and
   `timeout: float`. (Use either style above. The tests check `__required_keys__` and
   `__optional_keys__`.)
2. `Patch`: a TypedDict in which **all four** keys (`host`, `port`, `debug`, `timeout`, with
   the same types) are optional.
3. `with_defaults(cfg: Config) -> Config`: a **new** config where `debug` is `False` and `timeout` is `30.0` if they were missing. Keys that are present (even with a falsy value like
   `False` or `0.0`) stay as they are.
4. `apply_patch(cfg: Config, patch: Patch) -> Config`: a **new** config: `cfg` updated with the
   keys that are present in `patch`. Neither input changes.
5. `describe(cfg: Config) -> str`: `"host:port"`, followed by `" (debug)"` if `debug` is present and
   true, followed by `" timeout=<timeout>"` if `timeout` is present. Example: `"db:5432 (debug) timeout=2.5"`.

Import `TypedDict` and `NotRequired` from `typing`.

**Example**

```python
cfg: Config = {"host": "db", "port": 5432}
with_defaults(cfg)               # {'host': 'db', 'port': 5432, 'debug': False, 'timeout': 30.0}
apply_patch(cfg, {"port": 1})    # {'host': 'db', 'port': 1}
describe({"host": "db", "port": 5432, "debug": True, "timeout": 2.5})   # 'db:5432 (debug) timeout=2.5'
```
