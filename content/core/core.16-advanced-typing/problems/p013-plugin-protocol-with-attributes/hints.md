## Hint 1

In a protocol, how do you describe an attribute, as opposed to a method? (Think of a class body with only a name and a type, no value.) What is the body of the method, since a protocol only describes?

## Hint 2

The registry needs ordered storage and fast lookup by name: a `dict[str, Plugin]` keeps insertion order. `register` must check for a duplicate **before** storing. `run_all` is a loop that reassigns `text` to each plugin's result. What type is the empty-registry result, if you never enter the loop?

## Hint 3

```
class Plugin(Protocol):
    name: str
    version: int
    def run(self, text: str) -> str: ...

class PluginRegistry:
    __init__:   self._plugins: dict[str, Plugin] = {}
    register:   if plugin.name in self._plugins: raise ValueError(f"duplicate plugin: {plugin.name}")
                self._plugins[plugin.name] = plugin
    names:      list(self._plugins)
    get:        self._plugins.get(name)
    run_all:    for p in values: text = p.run(text) ; return text
    describe:   [f"{p.name} v{p.version}" ...]
```
