from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity: int) -> None:
        self._data: OrderedDict = OrderedDict()

    def get(self, key, default=None):
        return default

    def put(self, key, value) -> None:
        pass

    def __len__(self) -> int:
        return 0

    def keys(self) -> list:
        return []
