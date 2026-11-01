class Typed:
    """A data descriptor that only accepts values of the given types."""

    def __init__(self, *types, allow_bool=False):
        if not types:
            raise TypeError("Typed needs at least one type")
        for t in types:
            if not isinstance(t, type):
                raise TypeError(f"Typed expects classes, got {t!r}")
        self.types = types
        self.allow_bool = allow_bool or bool in types
        self.name = None
        self.owner_name = None

    def __set_name__(self, owner, name):
        self.owner_name = owner.__name__
        self.name = name

    def _label(self):
        return f"{self.owner_name}.{self.name}"

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        try:
            return instance.__dict__[self.name]
        except KeyError:
            raise AttributeError(f"{self._label()} has not been set") from None

    def __set__(self, instance, value):
        if isinstance(value, bool) and not self.allow_bool:
            ok = False
        else:
            ok = isinstance(value, self.types)
        if not ok:
            expected = " or ".join(t.__name__ for t in self.types)
            raise TypeError(f"{self._label()} must be {expected}, got {type(value).__name__}")
        instance.__dict__[self.name] = value

    def __delete__(self, instance):
        try:
            del instance.__dict__[self.name]
        except KeyError:
            raise AttributeError(f"{self._label()} has not been set") from None
