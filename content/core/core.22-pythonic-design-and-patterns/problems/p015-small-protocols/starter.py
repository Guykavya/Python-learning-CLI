from abc import ABC, abstractmethod


# NEW (write these, see problem.md): two small Protocols.
class Reader:
    pass


class Writer:
    pass


# OLD: one fat interface. Every class must provide all five methods, even if it can only do one.
class Storage(ABC):
    @abstractmethod
    def read(self, key): ...

    @abstractmethod
    def write(self, key, value): ...

    @abstractmethod
    def delete(self, key): ...

    @abstractmethod
    def keys(self): ...

    @abstractmethod
    def lock(self): ...


class MemoryStorage(Storage):
    def __init__(self):
        self.data = {}

    def read(self, key):
        return self.data[key]

    def write(self, key, value):
        self.data[key] = value

    def delete(self, key):
        del self.data[key]

    def keys(self):
        return list(self.data)

    def lock(self):
        pass


class ReadOnlyStorage(Storage):
    def __init__(self, data):
        self.data = dict(data)

    def read(self, key):
        return self.data[key]

    def write(self, key, value):
        raise NotImplementedError("read-only")

    def delete(self, key):
        raise NotImplementedError("read-only")

    def keys(self):
        return list(self.data)

    def lock(self):
        raise NotImplementedError("read-only")


def copy_all(src: Storage, dst: Storage):
    """Copy every key from src to dst. Return how many keys were copied."""
    count = 0
    for key in src.keys():
        dst.write(key, src.read(key))
        count += 1
    return count


def dump(src: Storage):
    """{key: value} for every key in src."""
    return {key: src.read(key) for key in src.keys()}


def save_all(dst: Storage, items):
    """Write every (key, value) of the dict items to dst. Return how many were written."""
    for key, value in items.items():
        dst.write(key, value)
    return len(items)
