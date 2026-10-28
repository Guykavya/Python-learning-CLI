# A generic Stack class

A stack of ints and a stack of strings have the same code. You do not want to write the class
twice, and you do not want `Stack` of "anything". You want `Stack[int]` to hand back `int`s
and `Stack[str]` to hand back `str`s. That is a **generic class**.

Write `class Stack(Generic[T])` in `solution.py` (with `T = TypeVar("T")`). It keeps its items in a
list (last pushed = first popped). Methods and hints:

- `__init__(self) -> None`: start empty.
- `push(self, item: T) -> None`: put an item on top.
- `pop(self) -> T`: remove and return the top item. If the stack is empty, raise `IndexError("pop from empty stack")`.
- `peek(self) -> T`: return the top item without removing it. Same error when empty.
- `is_empty(self) -> bool`
- `__len__(self) -> int`: number of items.

The tests check that `Stack` is really generic (`Stack.__parameters__` has one TypeVar, and
`Generic` is among the bases), and that `push`, `pop` and `peek` all use that **same** TypeVar.
On Python 3.12+ you may write `class Stack[T]:` instead of `Generic[T]`.

**Example**

```python
nums: Stack[int] = Stack()
nums.push(1)
nums.push(2)
nums.pop()      # 2   (a type checker says: int)
len(nums)       # 1
nums.peek()     # 1
```
