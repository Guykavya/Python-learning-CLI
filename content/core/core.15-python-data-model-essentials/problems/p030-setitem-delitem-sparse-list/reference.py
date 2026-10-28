class SparseList:
    def __init__(self, size, default=0):
        if size < 0:
            raise ValueError("size cannot be negative")
        self._size = size
        self.default = default
        self._data = {}          # only positions that differ from the default

    def _fix(self, index):
        if not isinstance(index, int):
            raise TypeError("SparseList indices must be integers")
        if index < 0:
            index += self._size
        if not 0 <= index < self._size:
            raise IndexError("SparseList index out of range")
        return index

    def __len__(self):
        return self._size

    def __getitem__(self, index):
        return self._data.get(self._fix(index), self.default)

    def __setitem__(self, index, value):
        index = self._fix(index)
        if value == self.default:
            self._data.pop(index, None)
        else:
            self._data[index] = value

    def __delitem__(self, index):
        index = self._fix(index)
        self._data = {(i - 1 if i > index else i): v for i, v in self._data.items() if i != index}
        self._size -= 1

    def __iter__(self):
        for i in range(self._size):
            yield self._data.get(i, self.default)

    @property
    def stored_count(self):
        return len(self._data)

    def __repr__(self):
        return f"SparseList({list(self)!r}, default={self.default!r})"
