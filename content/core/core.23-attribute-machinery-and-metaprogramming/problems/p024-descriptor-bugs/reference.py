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

    def __init__(self, kind, default=MISSING):
        self.kind = kind
        self.default = default
        self.name = None

    def __set_name__(self, owner, name):          # fix 2: learn the real name
        self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        try:
            return instance.__dict__[self.name]   # fix 1: per-instance storage
        except KeyError:
            if self.default is MISSING:
                raise AttributeError(f"{self.name} has not been set") from None
            return self.default

    def __set__(self, instance, value):
        if not isinstance(value, self.kind):
            raise TypeError(f"{self.name} must be {self.kind.__name__}, got {type(value).__name__}")
        instance.__dict__[self.name] = value


class Alias:
    """A second name for another attribute: reading and writing go to the target."""

    def __init__(self, target):
        self.target = target

    def __get__(self, instance, owner=None):
        if instance is None:                       # fix 3: class access
            return self
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
        extras = vars(self).get("extras", {})      # fix 4: never self.extras in here
        if name in extras:
            return extras[name]
        raise AttributeError(f"{type(self).__name__} has no attribute or extra {name!r}")
