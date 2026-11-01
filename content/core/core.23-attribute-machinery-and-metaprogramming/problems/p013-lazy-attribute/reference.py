class lazy:
    """Decorator: turn a one-argument method into an attribute computed on first read.

    A non-data descriptor: after the first read the value sits in the instance
    __dict__, which wins over this descriptor, so __get__ is not called again.
    """

    def __init__(self, func):
        self.func = func
        self.name = func.__name__
        self.__doc__ = func.__doc__

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        value = self.func(instance)
        instance.__dict__[self.name] = value
        return value
