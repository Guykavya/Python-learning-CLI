# A queue from two stacks

Build a FIFO queue using **only two Python lists used as stacks**: you may only `append`, `pop()` (from the end), look at `[-1]`, and check `len` or emptiness. No `deque`, no `pop(0)`, no `insert`, no slicing.

Write a class `QueueFromStacks` with:

| Method | Does |
|---|---|
| `push(x)` | adds `x` at the back |
| `pop()` | removes and returns the front item (the oldest) |
| `peek()` | returns the front item without removing it |
| `empty()` | `True` if the queue holds nothing |

`pop` and `peek` are never called on an empty queue.

Every operation must be **amortised `O(1)`**: a long run of operations costs `O(1)` per operation on average, even if one single `pop` is sometimes slow (chapter section 8, "A queue from two stacks"). The last test runs 300,000 operations with a time limit.

## Example

```python
>>> q = QueueFromStacks()
>>> q.push(1); q.push(2); q.push(3)
>>> q.pop()
1
>>> q.push(4)
>>> q.peek(), q.pop(), q.pop(), q.pop()
(2, 2, 3, 4)
>>> q.empty()
True
```

## How it is tested

5,000 random operations (fixed seed) run on your queue and on a `collections.deque` at the same time; every answer must agree. Another test reads your source code and fails if it uses `deque`, `pop(0)`, `insert` or slicing.

## Think about

Pouring a stack into another stack reverses it. When is it safe to pour the inbox into the outbox, and when would it mix up the order?
