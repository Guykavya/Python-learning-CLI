class ExpiringCache:
    def __init__(self, ttl, clock):
        self.clock = clock
        self._data = {}

    def set(self, key, value):
        self._data[key] = value

    def get(self, key, default=None):
        return self._data.get(key, default)

    def __len__(self):
        return len(self._data)
