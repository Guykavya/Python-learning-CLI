"""Validated fields for small model classes.

    class Product(Model):
        name = Field(str)
        price = Field(float, default=0.0)
        cost = Alias("price")        # a second name for price

    p = Product(name="pen", price=1.5, colour="blue")   # colour is an extra
    p.name, p.cost, p.colour         # ('pen', 1.5, 'blue')
"""

MISSING = object()


class Field:
    """A typed attribute with an optional default."""

    def __init__(self, kind, default=MISSING, name="field"):
        self.kind = kind
        self.default = default
        self.name = name
        self.value = default

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if self.value is MISSING:
            raise AttributeError(f"{self.name} has not been set")
        return self.value

    def __set__(self, instance, value):
        if not isinstance(value, self.kind):
            raise TypeError(f"{self.name} must be {self.kind.__name__}, got {type(value).__name__}")
        self.value = value


class Alias:
    """A second name for another attribute: reading and writing go to the target."""

    def __init__(self, target):
        self.target = target

    def __get__(self, instance, owner=None):
        return getattr(instance, self.target)

    def __set__(self, instance, value):
        setattr(instance, self.target, value)


class Model:
    """Base class: Model(**values) sets the Fields; other keywords become extras,
    readable as attributes too."""

    def __init__(self, **values):
        self.extras = {}
        names = self.field_names()
        for key, value in values.items():
            if key in names:
                setattr(self, key, value)
            else:
                self.extras[key] = value

    @classmethod
    def field_names(cls):
        names = []
        for klass in reversed(cls.__mro__):
            for key, value in vars(klass).items():
                if isinstance(value, Field) and key not in names:
                    names.append(key)
        return names

    def __getattr__(self, name):
        if name in self.extras:
            return self.extras[name]
        raise AttributeError(f"{type(self).__name__} has no attribute or extra {name!r}")
