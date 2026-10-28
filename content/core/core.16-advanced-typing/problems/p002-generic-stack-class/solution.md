## Approach

`class Stack(Generic[T])` declares that `Stack` has one type parameter. Every `T` inside the class means "the item type of *this* stack". When a user writes `Stack[int]`, the checker replaces `T` by `int` in every method: `push(item: int)`, `pop() -> int`.

At runtime the class behaves as an ordinary class: the `[int]` is only for the checker (it does not even check the items). The private list is annotated `list[T]` so that mypy can see that what comes out of the list is what went in.

## Code

```python
from typing import Generic, TypeVar

T = TypeVar("T")


class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self) -> T:
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items[-1]

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def __len__(self) -> int:
        return len(self._items)
```

## Complexity

`push`, `pop`, `peek`, `is_empty`, `len`: O(1) each (amortised for `push`). Space O(n).

## Another way

Python 3.12+: `class Stack[T]:` does the same without the `TypeVar` line and without `Generic`. You can also write `nums: Stack[int] = Stack()` to tell the checker which stack you mean when it cannot work it out from the first `push`.
