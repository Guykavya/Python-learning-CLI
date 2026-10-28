# A Plugin protocol with attributes and a registry

A text tool lets other people write plugins. You do not want to force them to inherit from
your base class (they may live in another package). You describe the **shape** of a plugin with a
Protocol that has both *data* (attributes) and *behaviour* (a method).

In `solution.py` write:

```python
class Plugin(Protocol):
    name: str
    version: int
    def run(self, text: str) -> str: ...
```

and a class `PluginRegistry` that uses it:

- `register(self, plugin: Plugin) -> None`: add the plugin. If a plugin with the same `name`
  is already registered, raise `ValueError(f"duplicate plugin: {name}")` and change nothing.
- `names(self) -> list[str]`: the names, in registration order.
- `get(self, name: str) -> Plugin | None`: the plugin with that name, or `None`.
- `run_all(self, text: str) -> str`: pass the text through every plugin in registration order
  (the output of one is the input of the next). With no plugins the text comes back unchanged.
- `describe(self) -> list[str]`: one string per plugin, like `"upper v2"` (`name`, a space, `v`,
  the version).

Import `Protocol` from `typing`.

The tests give you plugin classes that are plain classes, a dataclass, and a class with
class-level attributes. None of them inherit from `Plugin`. The tests also check the protocol
with `typing.get_protocol_members` and `typing.get_type_hints`.

**Example**

```python
class Upper:
    name = "upper"
    version = 2
    def run(self, text: str) -> str:
        return text.upper()

class Exclaim:
    def __init__(self):
        self.name = "exclaim"
        self.version = 1
    def run(self, text: str) -> str:
        return text + "!"

reg = PluginRegistry()
reg.register(Upper())
reg.register(Exclaim())
reg.run_all("hi")        # 'HI!'
reg.describe()           # ['upper v2', 'exclaim v1']
```
