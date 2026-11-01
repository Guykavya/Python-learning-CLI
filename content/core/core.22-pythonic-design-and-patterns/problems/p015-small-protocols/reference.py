from typing import Protocol, runtime_checkable


@runtime_checkable
class Reader(Protocol):
    def read(self, key): ...

    def keys(self): ...


@runtime_checkable
class Writer(Protocol):
    def write(self, key, value): ...


def copy_all(src: Reader, dst: Writer):
    count = 0
    for key in src.keys():
        dst.write(key, src.read(key))
        count += 1
    return count


def dump(src: Reader):
    return {key: src.read(key) for key in src.keys()}


def save_all(dst: Writer, items):
    for key, value in items.items():
        dst.write(key, value)
    return len(items)
