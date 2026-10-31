## Approach

The three item methods `__getitem__`, `__setitem__` and `__delitem__` are what `s[i]`, `s[i] = v` and `del s[i]` call. All three need the same index normalisation, so it lives in one helper.

`dict.get(key, default)` gives the sparse behaviour for free on reads. On writes, assigning the default is turned into a removal so the dict only ever holds non-default values. Deleting a position changes the positions of everything after it, so the dict is rebuilt with shifted keys.

## Code

```python
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
```

## Complexity

Read and write are O(1). `del` is O(k) where k is the number of stored entries (not the logical size). `iter` is O(size).

## Another way

Keep a sorted list of `(position, value)` pairs and use binary search (`bisect`): iteration in order becomes cheap and `del` is a simple shift of positions, but each read is O(log k) instead of O(1). A list subclass would store every default, which defeats the idea.
