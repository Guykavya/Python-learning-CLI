class Typed:
    """A data descriptor that only accepts values of the given types.

    Write __init__, __set_name__, __get__, __set__ and __delete__.
    """

    def __init__(self, *types, allow_bool=False):
        self.types = types

    def __set_name__(self, owner, name):
        pass

    def __get__(self, instance, owner=None):
        raise NotImplementedError

    def __set__(self, instance, value):
        raise NotImplementedError

    def __delete__(self, instance):
        raise NotImplementedError
