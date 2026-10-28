## Approach

A container class is a few special methods on top of ordinary data. Here the data is a fixed list and two numbers (`_start`, `_size`). The only tricky idea is **logical vs physical position**: the user thinks "item 0 is the oldest"; the list thinks in slots. The formula `(_start + i) % capacity` converts one to the other, and every method uses it.

`__len__` makes `len()` and truthiness work. `__iter__` written as a generator gives a **new** iterator for every loop. `__getitem__` handles negative indices and raises `IndexError` (which also makes the old iteration protocol work). `in`, `sum`, `sorted` and friends all use `__iter__`.

## Code

```python
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
```

## Complexity

`append`, `rb[i]`, `len` are O(1). Iteration is O(n). Memory is O(capacity).

## Another way

`collections.deque(maxlen=capacity)` does the same job in C and is what you would use in real code. Another version keeps the items in a plain list and does `del items[0]` when full: simpler but `append` becomes O(n).
