class Prop:
    """A pure-Python version of the built-in property."""

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel

    def __get__(self, instance, owner=None):
        raise NotImplementedError

    def setter(self, fset):
        raise NotImplementedError
