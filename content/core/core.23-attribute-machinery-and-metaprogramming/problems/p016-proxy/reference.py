class ReadOnlyProxy:
    """Read-only view of another object that counts attribute reads."""

    def __init__(self, target):
        object.__setattr__(self, "_target", target)
        object.__setattr__(self, "_counts", {})

    def __getattr__(self, name):
        # Only called when normal lookup failed. object.__getattribute__ never calls
        # __getattr__ again, so a half-built proxy (copy, pickle) gets AttributeError.
        target = object.__getattribute__(self, "_target")
        value = getattr(target, name)
        counts = object.__getattribute__(self, "_counts")
        counts[name] = counts.get(name, 0) + 1
        return value

    def __setattr__(self, name, value):
        raise AttributeError(f"cannot set {name!r}: read-only proxy")

    def __delattr__(self, name):
        raise AttributeError(f"cannot delete {name!r}: read-only proxy")

    def access_count(self, name):
        return self._counts.get(name, 0)

    def __repr__(self):
        return f"ReadOnlyProxy({self._target!r})"
