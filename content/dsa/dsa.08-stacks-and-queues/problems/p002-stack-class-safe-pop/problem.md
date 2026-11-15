# A Stack class with a safe pop

Write a class `Stack` that wraps a Python list (chapter section 2, "A small `Stack` class"). It needs:

| Method | Does | On an empty stack |
|---|---|---|
| `push(x)` | puts `x` on top | works |
| `pop()` | removes and returns the top item | raises `IndexError("pop from empty stack")` |
| `peek()` | returns the top item **without** removing it | raises `IndexError("peek at empty stack")` |
| `is_empty()` | `True` if there are no items | `True` |
| `len(s)` | number of items (define `__len__`) | `0` |

The error messages matter: a bare list says `pop from empty list`, which does not tell the reader *which* structure was empty. Raise your own `IndexError` with the exact messages above.

## Example

```python
>>> s = Stack()
>>> s.push(10); s.push(20)
>>> s.peek(), len(s)
(20, 2)
>>> s.pop(), s.pop()
(20, 10)
>>> s.is_empty()
True
>>> s.pop()
Traceback (most recent call last):
  ...
IndexError: pop from empty stack
```

## Constraints

- Every operation must be `O(1)`: work at the **end** of the list.
- Items can be any values, including `None` and `0`.

## Think about

Why should `peek` on an empty stack raise an error instead of returning `None`? (Hint: what if `None` was pushed?)
