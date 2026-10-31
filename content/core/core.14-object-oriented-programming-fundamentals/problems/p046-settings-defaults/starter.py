class Settings:
    debug = False
    host = "localhost"
    port = 8000
    workers = 1

    def __init__(self, **overrides):
        # TODO: check each override, store only those on the object
        pass

    @classmethod
    def names(cls):
        return []

    def as_dict(self):
        return {}

    def overrides(self):
        return {}

    def reset(self, name):
        pass

    def with_changes(self, **changes):
        return None


class DevSettings(Settings):
    pass


class ProductionSettings(Settings):
    pass
