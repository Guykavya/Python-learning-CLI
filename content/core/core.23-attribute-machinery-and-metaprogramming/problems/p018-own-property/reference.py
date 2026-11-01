class Prop:
    """A pure-Python version of the built-in property."""

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc
        self.name = fget.__name__ if fget is not None else "?"

    def __set_name__(self, owner, name):
        self.name = name

    def _error(self, instance, missing):
        return AttributeError(
            f"property {self.name!r} of {type(instance).__name__!r} object has no {missing}"
        )

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if self.fget is None:
            raise self._error(instance, "getter")
        return self.fget(instance)

    def __set__(self, instance, value):
        if self.fset is None:
            raise self._error(instance, "setter")
        self.fset(instance, value)

    def __delete__(self, instance):
        if self.fdel is None:
            raise self._error(instance, "deleter")
        self.fdel(instance)

    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.__doc__)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__)
