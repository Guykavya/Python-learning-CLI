class ExpiringCache:
    def __init__(self, ttl, clock):
        if ttl <= 0:
            raise ValueError("ttl must be positive")
        self.ttl = ttl
        self.clock = clock
        self._data = {}

    def _alive(self, entry, now):
        return now - entry[1] < self.ttl

    def set(self, key, value):
        self._data[key] = (value, self.clock())

    def get(self, key, default=None):
        entry = self._data.get(key)
        if entry is None or not self._alive(entry, self.clock()):
            return default
        return entry[0]

    def __len__(self):
        now = self.clock()
        return sum(1 for entry in self._data.values() if self._alive(entry, now))
