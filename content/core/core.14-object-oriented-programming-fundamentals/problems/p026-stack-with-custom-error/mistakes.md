- `def __init__(self, items=[])` and then `self._items = items`. The default list is shared by every
  stack made without arguments, so pushing to one stack changes them all.
- `self._items = items` when a list is passed. The stack and the caller now share one list. Copy it
  with `list(items)`.
- Letting the list's `IndexError` escape from `pop()`. The user of a stack should get a stack error.
- `is_empty` written as `return not self.peek()`. A stack that holds `0` or `""` is not empty.
- `class Stack(list)`. Then every list method (`insert`, `sort`, `s[0] = ...`) works on the stack
  too, and the "only the top" rule is gone.
- In `balanced`, forgetting the final `return stack.is_empty()`. `"(("` would then count as balanced.
- Catching every exception with a bare `except:` in `balanced`. Catch only `EmptyStackError`.
