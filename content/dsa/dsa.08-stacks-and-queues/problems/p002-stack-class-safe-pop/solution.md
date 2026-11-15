## Approach

A list already does everything a stack needs, as long as the top is the **end** of the list (`append` and `pop()` there are `O(1)`). The class adds two things: names that say what the operations mean, and clear errors on an empty stack.

## Code

```python
class Stack:
    def __init__(self):
        self._items = []

    def push(self, x):
        self._items.append(x)

    def pop(self):
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        if not self._items:
            raise IndexError("peek at empty stack")
        return self._items[-1]

    def is_empty(self):
        return not self._items

    def __len__(self):
        return len(self._items)
```

## Complexity

All operations are `O(1)` (amortised for `push`, because the list sometimes grows its storage). Memory is `O(n)` for `n` items.

## Another way

Instead of checking first, you can catch the list's own error and raise a clearer one:

```python
def pop(self):
    try:
        return self._items.pop()
    except IndexError:
        raise IndexError("pop from empty stack") from None
```

Both are fine. The "check first" version is easier to read; the `try` version is the "ask forgiveness" style from core.
