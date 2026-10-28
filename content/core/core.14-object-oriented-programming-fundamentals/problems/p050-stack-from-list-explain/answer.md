**1. What leaks.** `Stack(list)` inherits the whole interface of `list`: eleven public methods plus
operations like `s[i] = x`, `del s[i]`, slicing and `+`. Only three methods were chosen on purpose. In the output: `s.insert(0, 99)` put 99
at the bottom; `s.sort()` reordered the whole stack; `s[0] = "x"` overwrote the bottom item; and
`s.pop(0)` removed from the bottom. Others: `s.remove(x)`, `del s[1]`, `s.reverse()`, `s.extend(...)`,
slicing `s[1:3]`, `s.clear()`. None of these is "push, pop or peek at the top", yet every user of
`Stack` can call them, so the class cannot guarantee its own rule. Even `s + [7]` returns a plain
`list`, not a `Stack`.

**2. is-a vs has-a.** Inheritance is a promise: a subclass **is a** kind of its parent and can be used
everywhere the parent can (you can substitute it). A list allows random access and changes anywhere; a
stack forbids exactly that. So a stack is **not** a list. `isinstance(s, list)` being `True` tells
other code "go ahead, treat me as a list", and that code may then sort or insert into the undo history.
The real relation is **has-a**: a stack *has* a list to store its items.

**3. The fix (composition and delegation).**

```python
class Stack:
    def __init__(self):
        self._items = []          # "private": callers use the methods below

    def push(self, item):
        self._items.append(item)

    def pop(self):
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        if not self._items:
            raise IndexError("peek from empty stack")
        return self._items[-1]

    def is_empty(self):
        return not self._items

    def size(self):
        return len(self._items)

    def __repr__(self):
        return f"Stack({self._items!r})"
```

Each method **delegates** to the list. The public interface is now exactly the five stack operations.

**4. The cost.** Ravi writes a few one-line methods himself, and features like `len(s)`, `for x in s`
or `print(s)` do not come for free (a simple `size()` and `__repr__` cover what he needs; core.15
shows how to add `len()` and iteration on purpose). In return he gets a class that **cannot be
misused**, clearer error messages, and freedom to change the inside: he can later store items in a
`collections.deque` or add a maximum size, and no caller notices, because no caller ever touched the
list.

**5. When inheritance is right.** Use it when the subclass truly **is a** parent and keeps every
promise of the parent: `class InsufficientFunds(BankError)` is a bank error and can be caught as one;
`class Dog(Animal)` can be used anywhere an `Animal` is expected; a `class CaseInsensitiveDict(dict)`
that only changes how keys are stored still behaves like a dict everywhere. The test: "Can I hand my
object to any code written for the parent, and would that code still be correct?" If the answer is no
(as for the stack), use composition.
