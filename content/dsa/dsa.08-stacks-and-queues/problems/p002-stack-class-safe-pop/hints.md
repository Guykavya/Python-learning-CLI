## Hint 1

Keep the items in `self._items = []`. Which end of the list is the "top", if both `push` and `pop` must be `O(1)`?

## Hint 2

Check for emptiness **before** touching the list, and raise the error yourself:

```
def pop(self):
    if not self._items:
        raise IndexError("pop from empty stack")
    return self._items.pop()
```

`peek` is the same with `self._items[-1]` and its own message. `is_empty` returns `len(self._items) == 0`.
