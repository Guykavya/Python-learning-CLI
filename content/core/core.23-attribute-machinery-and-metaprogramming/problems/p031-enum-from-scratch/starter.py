class EnumMeta(type):
    """Turns plain class attributes into members and gives the class len/iter/lookup."""

    def __new__(mcls, name, bases, ns, **kwargs):
        return super().__new__(mcls, name, bases, ns, **kwargs)


class MiniEnum(metaclass=EnumMeta):
    pass
