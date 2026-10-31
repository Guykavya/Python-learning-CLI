class Registry:
    def __init__(self):
        self._classes = {}

    def __call__(self, cls=None, *, name=None):
        def decorate(klass):
            key = name if name is not None else klass.__name__.lower()
            if key in self._classes:
                raise ValueError(f"name {key!r} is already registered")
            self._classes[key] = klass
            klass.registered_name = key
            return klass

        if cls is None:          # used as @registry(name="x")
            return decorate
        return decorate(cls)     # used as @registry

    def __getitem__(self, name):
        try:
            return self._classes[name]
        except KeyError:
            raise KeyError(f"nothing registered as {name!r}") from None

    def __contains__(self, name):
        return name in self._classes

    def __len__(self):
        return len(self._classes)

    def names(self):
        return sorted(self._classes)


def auto_repr(cls):
    def __repr__(self):
        parts = ", ".join(f"{field}={getattr(self, field)!r}" for field in cls._fields)
        return f"{type(self).__name__}({parts})"

    cls.__repr__ = __repr__
    return cls
