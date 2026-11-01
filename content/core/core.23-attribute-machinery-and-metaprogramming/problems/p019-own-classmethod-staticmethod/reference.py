from types import MethodType


class ClassMethod:
    """Like the built-in classmethod: binds the function to the class."""

    def __init__(self, func):
        self.__func__ = func
        self.__doc__ = func.__doc__

    def __get__(self, instance, owner=None):
        if owner is None:
            owner = type(instance)
        return MethodType(self.__func__, owner)


class StaticMethod:
    """Like the built-in staticmethod: no binding at all."""

    def __init__(self, func):
        self.__func__ = func
        self.__doc__ = func.__doc__

    def __get__(self, instance, owner=None):
        return self.__func__

    def __call__(self, *args, **kwargs):
        return self.__func__(*args, **kwargs)
