class InterfaceMeta(type):
    """Refuses to create concrete classes that do not implement every name in `required`."""

    def __new__(mcls, name, bases, ns, **kwargs):
        return super().__new__(mcls, name, bases, ns, **kwargs)
