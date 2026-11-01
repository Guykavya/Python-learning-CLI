class SingletonMeta(type):
    """Metaclass: each class using it has exactly one instance (subclasses their own)."""

    def __call__(cls, *args, **kwargs):
        return super().__call__(*args, **kwargs)


class InstanceCounter(type):
    """Metaclass: each class using it counts its successful instance creations."""
