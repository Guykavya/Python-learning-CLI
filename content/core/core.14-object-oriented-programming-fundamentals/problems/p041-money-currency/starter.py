class CurrencyMismatchError(ValueError):
    pass


class Money:
    def __init__(self, minor, currency):
        # TODO: check and store (read-only properties)
        pass

    @classmethod
    def from_string(cls, text):
        return None

    def add(self, other):
        return None

    def subtract(self, other):
        return None

    def times(self, factor):
        return None

    def split(self, n):
        return []

    def format(self):
        return ""
