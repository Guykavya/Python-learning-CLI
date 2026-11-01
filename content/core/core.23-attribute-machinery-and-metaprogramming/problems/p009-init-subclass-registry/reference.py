class Plugin:
    registry = {}
    key = None

    def __init_subclass__(cls, /, key=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if key is None:
            return  # an abstract helper base: not registered
        if key in Plugin.registry:
            raise ValueError(f"duplicate plugin key {key!r} (already used by {Plugin.registry[key].__name__})")
        cls.key = key
        Plugin.registry[key] = cls

    @classmethod
    def create(cls, key, *args, **kwargs):
        try:
            plugin_class = Plugin.registry[key]
        except KeyError:
            known = ", ".join(sorted(Plugin.registry))
            raise KeyError(f"no plugin {key!r}; known: {known}") from None
        return plugin_class(*args, **kwargs)
