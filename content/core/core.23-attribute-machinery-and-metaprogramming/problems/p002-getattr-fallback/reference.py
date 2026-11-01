class Settings:
    def __init__(self, values, defaults=None):
        self._defaults = dict(defaults or {})
        for name, value in values.items():
            setattr(self, name, value)

    def __getattr__(self, name):
        # Called only when the normal lookup failed.
        # Never look up private or dunder names: copy, pickle and hasattr probe for
        # names like "__setstate__" on objects whose __init__ has not run yet.
        if name.startswith("_"):
            raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")
        defaults = self._defaults
        if name in defaults:
            return defaults[name]
        raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")
