def find_owner(cls, name):
    for klass in cls.__mro__:
        if name in vars(klass):
            return klass
    return None


def _type_defines(obj, method):
    # The protocol is looked up on the type, in the type's own MRO.
    return any(method in vars(klass) for klass in type(obj).__mro__)


def classify(cls, name):
    owner = find_owner(cls, name)
    if owner is None:
        return "missing"
    raw = vars(owner)[name]
    if _type_defines(raw, "__set__") or _type_defines(raw, "__delete__"):
        return "data descriptor"
    if _type_defines(raw, "__get__"):
        return "non-data descriptor"
    return "plain"


def describe(cls):
    return {name: classify(cls, name) for name in vars(cls) if not name.startswith("__")}
