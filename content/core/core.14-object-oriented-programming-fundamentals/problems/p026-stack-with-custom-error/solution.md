## Approach

The stack *has* a list; it is not a list. So we keep a list in an attribute, `self._items`, and
offer only the stack operations (chapter section 14). A user cannot call `insert(0, x)` or
`sort()` and break the "only the top" rule.

The end of the list is the top: `append` is push, `pop()` is pop, `[-1]` is peek. All three are
fast.

**Our own exception.** An empty list raises `IndexError: pop from empty list`, which talks about
lists, a detail the user should not need to know. A class-specific `EmptyStackError` says what
really went wrong, and callers can catch exactly that (section 17). The class body can be just a
docstring.

**The starting items.** `items=None` and then `list(items)` gives each stack a new list that is a
copy. This avoids the mutable default trap and the aliasing trap at once.

**`balanced`** is the classic use of a stack: the most recent opening bracket must be closed first.
A closing bracket with an empty stack is exactly the `EmptyStackError` case, so we catch it and
answer `False`. At the end, leftover opening brackets mean `False` too.

## Code

```python
class EmptyStackError(Exception):
    """Raised when you pop or peek at an empty stack."""


class Stack:
    def __init__(self, items=None):
        self._items = [] if items is None else list(items)

    def push(self, item):
        self._items.append(item)

    def pop(self):
        if not self._items:
            raise EmptyStackError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        if not self._items:
            raise EmptyStackError("peek at empty stack")
        return self._items[-1]

    def is_empty(self):
        return not self._items

    def size(self):
        return len(self._items)

    def to_list(self):
        return list(self._items)


PAIRS = {")": "(", "]": "[", "}": "{"}


def balanced(text):
    stack = Stack()
    for ch in text:
        if ch in "([{":
            stack.push(ch)
        elif ch in PAIRS:
            try:
                top = stack.pop()
            except EmptyStackError:
                return False
            if top != PAIRS[ch]:
                return False
    return stack.is_empty()
```

## Complexity

Every stack method is O(1), except `to_list` and the constructor, which copy: O(n).
`balanced` is O(n) for a text of length n.

## Another way

Instead of checking first, `pop` could try the list's `pop()` and turn the error into ours:

```python
def pop(self):
    try:
        return self._items.pop()
    except IndexError:
        raise EmptyStackError("pop from empty stack") from None
```

`from None` hides the list's `IndexError` from the traceback (section 18). Both versions are fine.
