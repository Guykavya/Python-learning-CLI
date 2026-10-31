from collections.abc import Callable
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class Repository(Generic[K, V]):
    def __init__(self) -> None:
        self._data: dict[K, V] = {}

    def add(self, key: K, value: V) -> None:
        if key in self._data:
            raise KeyError(key)
        self._data[key] = value

    def get(self, key: K) -> V | None:
        return self._data.get(key)

    def require(self, key: K) -> V:
        return self._data[key]

    def remove(self, key: K) -> V:
        return self._data.pop(key)

    def find(self, predicate: Callable[[V], bool]) -> list[V]:
        return [v for v in self._data.values() if predicate(v)]

    def all(self) -> list[V]:
        return list(self._data.values())

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, key: K) -> bool:
        return key in self._data
