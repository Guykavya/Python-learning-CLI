# Min stack

Write a class `MinStack` with four operations, **all `O(1)`**:

| Method | Does |
|---|---|
| `push(x)` | puts `x` on top |
| `pop()` | removes the top item and returns it |
| `top()` | returns the top item without removing it |
| `get_min()` | returns the smallest item currently in the stack |

`pop`, `top` and `get_min` on an empty stack raise `IndexError`.

Scanning the stack in `get_min` is `O(n)`; the last test calls `get_min` 100,000 times on a stack of 100,000 items with a time limit. Store extra information with each item instead (chapter section 8, "A stack that knows its minimum").

## Example

```python
>>> m = MinStack()
>>> for x in (5, 3, 7, 3, 8):
...     m.push(x)
>>> m.get_min()
3
>>> m.pop(), m.pop(), m.get_min()
(8, 3, 3)
>>> m.pop(), m.pop(), m.get_min()
(7, 3, 5)
>>> m.top()
5
```

## How it is tested

Besides the example, 5,000 random operations (with a fixed seed) are run on your `MinStack` and on a plain Python list at the same time; after every step the answers must agree.

## Think about

When an item is popped, the minimum of what is left must be known **without looking at the other items**. Where could that answer already be written down?
