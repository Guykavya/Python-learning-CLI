## Approach

A TypedDict key is *required* by default. Two ways to loosen that:

- `NotRequired[T]` on a single key (Python 3.11+): `debug: NotRequired[bool]`.
- `total=False` on the class: every key declared **in that class** becomes optional. To mix required and optional keys with `total=False`, put the required keys in a base class and the optional ones in a subclass.

`Patch` has only optional keys, so `class Patch(TypedDict, total=False)` is the shortest way. Python stores the result in `__required_keys__` and `__optional_keys__` (the tests read them).

Inside the functions, "is the key there?" is answered with `in`, not with truthiness: `cfg.get("debug")` is `False` both when `debug` is missing and when it is `False`, and `timeout=0.0` is falsy yet present. `apply_patch` builds the new dict key by key so that the checker can follow the types; at runtime `{**cfg, **patch}` is the same thing.

## Code

```python
from typing import NotRequired, TypedDict


class Config(TypedDict):
    host: str
    port: int
    debug: NotRequired[bool]
    timeout: NotRequired[float]


class Patch(TypedDict, total=False):
    host: str
    port: int
    debug: bool
    timeout: float


def with_defaults(cfg: Config) -> Config:
    out = Config(host=cfg["host"], port=cfg["port"])
    out["debug"] = cfg.get("debug", False)
    out["timeout"] = cfg.get("timeout", 30.0)
    return out


def apply_patch(cfg: Config, patch: Patch) -> Config:
    out = Config(host=cfg["host"], port=cfg["port"])
    if "debug" in cfg:
        out["debug"] = cfg["debug"]
    if "timeout" in cfg:
        out["timeout"] = cfg["timeout"]
    if "host" in patch:
        out["host"] = patch["host"]
    if "port" in patch:
        out["port"] = patch["port"]
    if "debug" in patch:
        out["debug"] = patch["debug"]
    if "timeout" in patch:
        out["timeout"] = patch["timeout"]
    return out


def describe(cfg: Config) -> str:
    text = f"{cfg['host']}:{cfg['port']}"
    if cfg.get("debug") is True:
        text += " (debug)"
    if "timeout" in cfg:
        text += f" timeout={cfg['timeout']}"
    return text
```

## Complexity

All functions O(k) for k keys (a small constant here).

## Another way

Class-based, with inheritance:

```python
class _ConfigBase(TypedDict):
    host: str
    port: int

class Config(_ConfigBase, total=False):
    debug: bool
    timeout: float
```

This is the only way on Python 3.10 and older. For `apply_patch` the short form `return {**cfg, **patch}` has the same result at runtime and mypy accepts it too; the reference copies key by key only to make each step visible.
