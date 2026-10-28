## Hint 1

A Python list already has `append` and `pop` at its end. If the end of the list is the top of the
stack, which list methods do `push` and `pop` become? What does `[].pop()` raise, and why should your
class turn that into its own error instead?

## Hint 2

Why is `def __init__(self, items=[])` dangerous? The default list is made **once**, when the `def`
runs, and every stack would share it. Use `items=None`, and inside: if it is `None` make `[]`,
otherwise make `list(items)`, a new copy.

## Hint 3

```
pop():
    if the list is empty: raise EmptyStackError("pop from empty stack")
    return self._items.pop()

balanced(text):
    stack = Stack()
    for ch in text:
        if ch is an opening bracket: stack.push(ch)
        elif ch is a closing bracket:
            try: top = stack.pop()
            except EmptyStackError: return False
            if top is not the partner of ch: return False
    return stack.is_empty()
```
