class Plugin:
    pass


class PluginRegistry:
    def __init__(self):
        self._plugins = {}

    def register(self, plugin):
        self._plugins[plugin.name] = plugin

    def names(self):
        return list(self._plugins)

    def get(self, name):
        return self._plugins.get(name)

    def run_all(self, text):
        return text

    def describe(self):
        return []
