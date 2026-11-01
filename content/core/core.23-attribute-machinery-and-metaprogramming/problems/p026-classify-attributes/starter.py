def find_owner(cls, name):
    """First class in cls.__mro__ whose own __dict__ has name, else None."""
    return None


def classify(cls, name):
    """'data descriptor', 'non-data descriptor', 'plain' or 'missing'. Never call getattr(cls, name)."""
    return "missing"


def describe(cls):
    """{name: classification} for the names in cls's own __dict__ that do not start with '__'."""
    return {}
