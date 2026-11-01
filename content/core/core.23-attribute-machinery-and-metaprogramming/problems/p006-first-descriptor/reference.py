class Upper:
    """Non-data descriptor: the upper-case version of another attribute."""

    def __init__(self, source):
        self.source = source

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return getattr(instance, self.source).upper()


class Fahrenheit:
    """Data descriptor: reads and writes the owner's `celsius` attribute."""

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return instance.celsius * 9 / 5 + 32

    def __set__(self, instance, value):
        instance.celsius = (value - 32) * 5 / 9
