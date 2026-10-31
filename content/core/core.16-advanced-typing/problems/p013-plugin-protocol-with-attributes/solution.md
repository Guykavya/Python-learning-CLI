## Approach

A protocol may declare **attributes** as well as methods: `name: str` and `version: int` with no value. Any object with a `name` that is a `str`, a `version` that is an `int` and a `run(text) -> str` method fits, whether the attributes are class-level (`Upper`), set in `__init__` (`Exclaim`) or dataclass fields (`Strip`). Nobody inherits from `Plugin`: the checker compares shapes.

The registry stores plugins in a `dict[str, Plugin]`: insertion order gives the run order, and the dict gives lookup by name. `register` checks for a duplicate first, so a rejected plugin leaves the registry untouched. `run_all` threads the text through the plugins, so with no plugins the loop never runs and the original text is returned.

## Code

```python
from typing import Protocol


class Plugin(Protocol):
    name: str
    version: int

    def run(self, text: str) -> str: ...


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        if plugin.name in self._plugins:
            raise ValueError(f"duplicate plugin: {plugin.name}")
        self._plugins[plugin.name] = plugin

    def names(self) -> list[str]:
        return list(self._plugins)

    def get(self, name: str) -> Plugin | None:
        return self._plugins.get(name)

    def run_all(self, text: str) -> str:
        for plugin in self._plugins.values():
            text = plugin.run(text)
        return text

    def describe(self) -> list[str]:
        return [f"{p.name} v{p.version}" for p in self._plugins.values()]
```

## Complexity

`register`, `get`: O(1). `names`, `describe`: O(n). `run_all`: O(n) plugin calls.

## Another way

If plugins must not be able to change their own `name`, declare it read-only with a property in the protocol:

```python
@property
def name(self) -> str: ...
```

Then a frozen dataclass or a class with a read-only property also fits. A plain `name: str` is a *settable* attribute, which means a class where `name` is read-only would be rejected by the checker. Another option is an abstract base class (`class Plugin(ABC)`): it gives clear errors at class-creation time but forces inheritance.
