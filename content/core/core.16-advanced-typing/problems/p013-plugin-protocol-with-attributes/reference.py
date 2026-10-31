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
