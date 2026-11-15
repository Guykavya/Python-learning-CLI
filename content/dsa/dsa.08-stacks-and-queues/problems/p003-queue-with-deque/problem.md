# A Queue class with a deque

Write a class `Queue` that stores its items in a `collections.deque` (chapter section 3, "A queue class"):

| Method | Does | On an empty queue |
|---|---|---|
| `enqueue(x)` | adds `x` at the back | works |
| `dequeue()` | removes and returns the front item (the oldest) | raises `IndexError("dequeue from empty queue")` |
| `front()` | returns the front item without removing it | raises `IndexError("front of empty queue")` |
| `is_empty()` | `True` if there are no items | `True` |
| `len(q)` | number of items | `0` |

Every operation must be `O(1)`. That is why you use a deque: `deque.popleft()` is `O(1)`, while `list.pop(0)` shifts every other item and costs `O(n)`. The tests check that the items live in a deque and run 100,000 operations with a time limit.

## Example

```python
>>> q = Queue()
>>> for name in ("Asha", "Ben", "Chitra"):
...     q.enqueue(name)
>>> q.front(), len(q)
('Asha', 3)
>>> q.dequeue(), q.dequeue()
('Asha', 'Ben')
>>> q.dequeue(), q.is_empty()
('Chitra', True)
```

## Constraints

- Up to `10**5` items at a time.
- Items can be any values, including `None`.

## Think about

A queue is "first in, first out". Which end of the deque do you add to, and which end do you remove from? Does it matter which choice you make, as long as you are consistent?
