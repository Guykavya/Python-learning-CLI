from abc import ABC, abstractmethod


class Storage(ABC):
    # TODO: four abstract methods: get, set, delete, keys

    def get_or(self, key, default=None):
        return None

    def contains(self, key):
        return False

    def pop(self, key):
        return None

    def items(self):
        return []

    def update(self, pairs):
        pass

    def count(self):
        return 0


class MemoryStorage(Storage):
    def __init__(self, initial=None):
        pass


class PrefixStorage(Storage):
    def __init__(self, inner, prefix):
        pass
