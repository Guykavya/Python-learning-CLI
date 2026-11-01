from types import MethodType


class ClassMethod:
    """Like the built-in classmethod: binds the function to the class."""

    def __init__(self, func):
        self.__func__ = func

    def __get__(self, instance, owner=None):
        raise NotImplementedError


class StaticMethod:
    """Like the built-in staticmethod: no binding at all."""

    def __init__(self, func):
        self.__func__ = func

    def __get__(self, instance, owner=None):
        raise NotImplementedError
