## Approach

Delegating to a stored list gives you all the sequence behaviour (negatives, `IndexError`) for free. Python builds `for`, `in`, `list()` and truthiness on top of `__getitem__` and `__len__`.

## Code

```python
class Playlist:
    def __init__(self, songs):
        self._songs = list(songs)

    def __len__(self):
        return len(self._songs)

    def __getitem__(self, index):
        return self._songs[index]
```

## Complexity

O(1) for `len` and indexing.

## Another way

Subclass `list`, or use `collections.abc.Sequence` (later) to get more methods from just these two.
