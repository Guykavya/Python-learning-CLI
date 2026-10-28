class Repository:
    def __init__(self):
        self._data = {}

    def add(self, key, value):
        self._data[key] = value

    def get(self, key):
        return self._data.get(key)

    def require(self, key):
        return self._data[key]

    def remove(self, key):
        return self._data.pop(key)

    def find(self, predicate):
        return []

    def all(self):
        return []

    def __len__(self):
        return len(self._data)

    def __contains__(self, key):
        return key in self._data
