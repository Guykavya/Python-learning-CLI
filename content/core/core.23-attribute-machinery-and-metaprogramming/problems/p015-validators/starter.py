from abc import ABC, abstractmethod


class Validator(ABC):
    """Base descriptor: stores per instance, calls self.validate(value) before storing."""

    def __set_name__(self, owner, name):
        pass

    def __get__(self, instance, owner=None):
        raise NotImplementedError

    def __set__(self, instance, value):
        raise NotImplementedError

    def validate(self, value):
        """Raise TypeError or ValueError if value is not acceptable."""


class Range(Validator):
    def __init__(self, min_value=None, max_value=None):
        pass


class OneOf(Validator):
    def __init__(self, *options):
        pass


class NonEmptyStr(Validator):
    def __init__(self, max_len=None):
        pass
