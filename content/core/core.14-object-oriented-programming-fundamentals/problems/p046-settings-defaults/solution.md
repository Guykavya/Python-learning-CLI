## Approach

This problem is attribute lookup put to work (chapter sections 5 and 9).

- **Defaults are class attributes.** Every object can read them, and there is one copy.
- **An override is an instance attribute.** Assigning `self.port = 9000` puts `port` into the
  object's own `__dict__`, which is searched first, so it hides the class value for that object only.
- **A subclass changes defaults** by defining the same class attributes again. Lookup goes object →
  its class → parents, so a `ProductionSettings` object finds `port = 80` before `Settings.port`.

The key rule: `__init__` stores **only** the overrides. If it copied every default onto the object,
`overrides()` could not tell what was given, `reset` would have nothing to fall back to, and changing
`Settings.workers` later would not reach existing objects.

`setattr`, `getattr`, `delattr` and `vars` handle attribute names held in variables. `reset` deletes
the instance attribute only; the class attribute stays, so the default "shows through" again.

`with_changes` uses `type(self)(...)`, so a `ProductionSettings` produces a `ProductionSettings`.
The `{**a, **b}` merge lets later keys (the changes) win.

## Code

```python
class Settings:
    debug = False
    host = "localhost"
    port = 8000
    workers = 1

    def __init__(self, **overrides):
        for name, value in overrides.items():
            self._check(name)
            default = getattr(type(self), name)
            if type(value) is not type(default):
                raise TypeError(f"{name} must be {type(default).__name__}, got {type(value).__name__}")
            setattr(self, name, value)

    @classmethod
    def names(cls):
        return sorted(
            name for name in dir(cls)
            if not name.startswith("_") and not callable(getattr(cls, name))
        )

    def _check(self, name):
        if name not in self.names():
            raise TypeError(f"unknown setting {name!r}")

    def as_dict(self):
        return {name: getattr(self, name) for name in self.names()}

    def overrides(self):
        return dict(vars(self))

    def reset(self, name):
        self._check(name)
        if name in vars(self):
            delattr(self, name)

    def with_changes(self, **changes):
        return type(self)(**{**self.overrides(), **changes})


class DevSettings(Settings):
    debug = True


class ProductionSettings(Settings):
    host = "0.0.0.0"
    port = 80
    workers = 4
```

`self.names()` works from an instance too: a classmethod receives the object's class as `cls`.
`TypeError` is the error Python itself raises for an unexpected keyword argument, so callers get
the error they already expect.

## Complexity

`names()` is O(a log a) for a attributes on the class. `__init__` calls it once per override;
`as_dict` is O(s) lookups for s settings.

## Another way

You could keep the defaults in a dict (`DEFAULTS = {...}`) and the overrides in `self._values`, with
a `get(name)` method. That works, but you lose `s.port` attribute syntax and subclass defaults
need a dict merge. Real projects often use `dataclasses` (core.15) or a library such as
`pydantic-settings` for this job.
