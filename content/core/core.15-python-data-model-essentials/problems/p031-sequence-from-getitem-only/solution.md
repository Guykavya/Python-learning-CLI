## Approach

The old sequence protocol: `iter(obj)` returns an iterator that calls `obj.__getitem__(0)`, `(1)`, ... and ends on the first `IndexError`. That is why `IndexError` (not `KeyError`) is the right signal for a bad index in a sequence, and why `__getitem__` must **never** return a value for indices past the end.

`reversed(obj)` uses another rule: if there is no `__reversed__`, it needs `__len__` and `__getitem__`, and it calls `obj[len-1]`, `obj[len-2]`, ..., `obj[0]`. `Backwards` supplies exactly that, and because it only uses `len()` and `[]` on the wrapped object it also wraps another `Backwards`.

## Code

```python
class Multiples:
    """Only __getitem__: no __iter__, no __len__."""

    def __init__(self, step, count):
        self.step = step
        self.count = count

    def __getitem__(self, index):
        if not isinstance(index, int):
            raise TypeError("indices must be integers")
        if not 0 <= index < self.count:
            raise IndexError(index)
        return self.step * (index + 1)


class Backwards:
    """Reads another sequence from the end. Needs __len__ and __getitem__ (reversed() uses them)."""

    def __init__(self, seq):
        self.seq = seq

    def __len__(self):
        return len(self.seq)

    def __getitem__(self, index):
        if not isinstance(index, int):
            raise TypeError("indices must be integers")
        if not 0 <= index < len(self.seq):
            raise IndexError(index)
        return self.seq[len(self.seq) - 1 - index]
```

## Complexity

`Multiples[i]` is O(1); iterating n items is O(n). `Backwards` indexing is O(1) when the wrapped sequence indexes in O(1).

## Another way

Define `__iter__` as a generator (and `__len__`): clearer for readers, and the preferred way today. The `__getitem__`-only form is worth knowing because standard-library and older code uses it, and because `reversed()` and `random.choice()` rely on `__len__` plus `__getitem__`.
