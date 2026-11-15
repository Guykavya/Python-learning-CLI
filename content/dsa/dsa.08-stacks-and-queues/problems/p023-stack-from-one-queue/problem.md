# A stack from one queue

Build a LIFO stack on top of a **queue**. A queue only lets you add at the back and take from the front, so the only operations you may use on it are:

- `q.append(x)` (enqueue at the back),
- `q.popleft()` (dequeue from the front),
- `q[0]` (look at the front),
- `len(q)` and `if q:`.

Anything else (`pop`, `appendleft`, `rotate`, `q[-1]`, iterating over `q`, ...) is **not** a queue operation.

Write a class `StackFromQueue` whose constructor is `StackFromQueue(queue_factory=deque)`. Create **every** queue you need by calling `queue_factory()` (normally that just gives a `deque`). The tests pass a special deque that records every forbidden call, so they can check that you only used queue operations.

| Method | Does |
|---|---|
| `push(x)` | puts `x` on top |
| `pop()` | removes and returns the top (the newest item) |
| `top()` | returns the top without removing it |
| `empty()` | `True` if nothing is stored |

`pop` and `top` are never called on an empty stack.

## Example

```python
>>> s = StackFromQueue()
>>> s.push(1); s.push(2); s.push(3)
>>> s.pop(), s.pop(), s.top()
(3, 2, 1)
>>> s.empty()
False
```

## Constraints

- Up to 2,000 items at a time. `push` may be `O(n)`; `pop` and `top` should be `O(1)` (chapter section 8, "A stack from a queue").

## Think about

After a push, you want the new item at the **front** of the queue. With only "take from the front, put at the back", how many items must go round the queue so that the new one ends up in front?
