## Approach

Keep the queue ordered newest-first. A new item enters at the back; then rotate all the **older** items (there are `len - 1` of them) from the front to the back, one by one. Now the new item is at the front, followed by the older items in their old order, so the queue front is always the stack top.

## Code

```python
from collections import deque


class StackFromQueue:
    def __init__(self, queue_factory=deque):
        self.q = queue_factory()

    def push(self, x):
        self.q.append(x)
        for _ in range(len(self.q) - 1):       # move all older items behind x
            self.q.append(self.q.popleft())

    def pop(self):
        return self.q.popleft()

    def top(self):
        return self.q[0]

    def empty(self):
        return not self.q
```

## Complexity

`push` is `O(n)` (it rotates `n - 1` items); `pop`, `top` and `empty` are `O(1)`. Memory `O(n)`.

## Another way

Make `pop` the expensive one instead: push is a plain `append`, and `pop` moves `len - 1` items from the front to the back, then takes the front (the newest). With two queues you can also move the items into a second queue and swap the names. All versions have one `O(n)` operation: a queue cannot give you LIFO order for free. Compare with problem 22, where the reverse direction is amortised `O(1)`.
