def defined_in(cls, name):
    if not isinstance(cls, type):
        raise TypeError("defined_in() needs a class")
    for klass in cls.__mro__:
        if name in vars(klass):
            return klass
    return None


def all_definitions(cls, name):
    if not isinstance(cls, type):
        raise TypeError("all_definitions() needs a class")
    return [klass.__name__ for klass in cls.__mro__ if name in vars(klass)]
