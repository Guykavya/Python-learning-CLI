class InterfaceMeta(type):
    def __new__(mcls, name, bases, ns, abstract=False, **kwargs):
        cls = super().__new__(mcls, name, bases, ns, **kwargs)
        cls._abstract = abstract                 # stored on this class only
        if not abstract:
            missing = [req for req in cls.requirements if not _implemented(cls, req)]
            if missing:
                raise TypeError(f"{name} must implement: {', '.join(sorted(missing))}")
        return cls

    def __init__(cls, name, bases, ns, abstract=False, **kwargs):
        super().__init__(name, bases, ns, **kwargs)

    @property
    def is_abstract(cls):
        return vars(cls).get("_abstract", False)

    @property
    def requirements(cls):
        names = set()
        for klass in cls.__mro__:
            names.update(vars(klass).get("required", ()))
        return tuple(sorted(names))

    def __call__(cls, *args, **kwargs):
        if cls.is_abstract:
            raise TypeError(f"{cls.__name__} is abstract")
        return super().__call__(*args, **kwargs)


def _implemented(cls, name):
    for klass in cls.__mro__:
        if name in vars(klass):
            return vars(klass)[name] is not None
    return False
