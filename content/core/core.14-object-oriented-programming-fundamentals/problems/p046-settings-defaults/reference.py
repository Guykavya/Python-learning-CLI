class Settings:
    debug = False
    host = "localhost"
    port = 8000
    workers = 1

    def __init__(self, **overrides):
        for name, value in overrides.items():
            self._check(name)
            default = getattr(type(self), name)
            if type(value) is not type(default):
                raise TypeError(f"{name} must be {type(default).__name__}, got {type(value).__name__}")
            setattr(self, name, value)

    @classmethod
    def names(cls):
        return sorted(
            name for name in dir(cls)
            if not name.startswith("_") and not callable(getattr(cls, name))
        )

    def _check(self, name):
        if name not in self.names():
            raise TypeError(f"unknown setting {name!r}")

    def as_dict(self):
        return {name: getattr(self, name) for name in self.names()}

    def overrides(self):
        return dict(vars(self))

    def reset(self, name):
        self._check(name)
        if name in vars(self):
            delattr(self, name)

    def with_changes(self, **changes):
        return type(self)(**{**self.overrides(), **changes})


class DevSettings(Settings):
    debug = True


class ProductionSettings(Settings):
    host = "0.0.0.0"
    port = 80
    workers = 4
