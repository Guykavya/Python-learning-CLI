class Locked:
    def __init__(self, **fields):
        if self.__dict__.get("_locked", False):
            raise AttributeError(f"{type(self).__name__} is locked: cannot run __init__ again")
        for name, value in fields.items():
            object.__setattr__(self, name, value)
        object.__setattr__(self, "_locked", True)

    def __setattr__(self, name, value):
        if self.__dict__.get("_locked", False):
            raise AttributeError(f"cannot set {name!r}: {type(self).__name__} is locked")
        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        raise AttributeError(f"cannot delete {name!r}: {type(self).__name__} is locked")

    def __repr__(self):
        parts = [f"{k}={v!r}" for k, v in self.__dict__.items() if k != "_locked"]
        return f"{type(self).__name__}({', '.join(parts)})"
