class RingBuffer:
    def __init__(self, capacity):
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self.capacity = capacity
        self._items = [None] * capacity
        self._start = 0      # index of the oldest item
        self._size = 0

    def append(self, item):
        if self._size < self.capacity:
            self._items[(self._start + self._size) % self.capacity] = item
            self._size += 1
        else:
            self._items[self._start] = item          # overwrite the oldest
            self._start = (self._start + 1) % self.capacity

    def is_full(self):
        return self._size == self.capacity

    def __len__(self):
        return self._size

    def __getitem__(self, index):
        if not isinstance(index, int):
            raise TypeError("RingBuffer indices must be integers")
        if index < 0:
            index += self._size
        if not 0 <= index < self._size:
            raise IndexError("RingBuffer index out of range")
        return self._items[(self._start + index) % self.capacity]

    def __iter__(self):
        for i in range(self._size):
            yield self._items[(self._start + i) % self.capacity]

    def __repr__(self):
        return f"RingBuffer({list(self)!r}, capacity={self.capacity})"
