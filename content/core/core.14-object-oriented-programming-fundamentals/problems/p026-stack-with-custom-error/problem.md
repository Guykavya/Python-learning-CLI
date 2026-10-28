# A stack with its own error

A **stack** is a pile: you put things on top (`push`) and take them from the top (`pop`). The last
thing in is the first thing out. Write it as a class in `solution.py`, plus its own exception and a
small function that uses it.

**`EmptyStackError`** is a subclass of `Exception`.

**`Stack(items=None)`** keeps its items in a list attribute.

- `items` is an optional iterable of starting items, bottom first. The stack must keep its **own
  copy**: changing the list you passed in later must not change the stack.
- `push(item)` puts `item` on top. Returns `None`.
- `pop()` removes and returns the top item.
- `peek()` returns the top item without removing it.
- `pop()` and `peek()` on an empty stack raise `EmptyStackError` (not `IndexError`). The message
  must contain the word `empty`.
- `is_empty()` returns `True` or `False`.
- `size()` returns the number of items.
- `to_list()` returns a new list of the items, bottom first.

**`balanced(text)`** returns `True` when every bracket in `text` is closed by the matching bracket in
the right order, and `False` otherwise. The brackets are `()`, `[]` and `{}`; ignore every other
character. Use a `Stack`: push each opening bracket; for a closing bracket, `pop()` and compare.
A closing bracket with nothing to match makes `pop()` raise `EmptyStackError`. Catch it and
return `False`.

**Example**

```python
s = Stack([1, 2])
s.push(3)
s.peek()          # 3
s.pop()           # 3
s.pop()           # 2
s.size()          # 1
s.to_list()       # [1]
s.pop()           # 1
s.is_empty()      # True
s.pop()           # EmptyStackError: pop from empty stack

balanced("f(a[0]) + {x}")   # True
balanced("(]")              # False
balanced("())")             # False  (the second ')' has nothing to match)
balanced("((")              # False  (two brackets never closed)
```
