class Settings:
    def __init__(self, values, defaults=None):
        self._values = dict(values)
        self._defaults = dict(defaults or {})

    def __getattr__(self, name):
        # TODO: values first, then defaults, else AttributeError.
        # Careful with names that start with "_" (see the problem statement).
        raise NotImplementedError("write Settings.__getattr__")
