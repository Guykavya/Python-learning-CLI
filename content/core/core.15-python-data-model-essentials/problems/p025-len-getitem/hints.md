## Hint 1

`for s in p` on an object with only `__getitem__`: Python calls `p[0]`, `p[1]`, ... until `IndexError`. So what must `__getitem__` do for an index that is too large?

## Hint 2

Store `self._songs = list(songs)`. Then `__len__` is `len(self._songs)` and `__getitem__` can simply return `self._songs[index]`: the list already raises `IndexError` and handles negatives.

## Hint 3

```
__init__: self._songs = list(songs)
__len__:  return len(self._songs)
__getitem__(self, index): return self._songs[index]
```
