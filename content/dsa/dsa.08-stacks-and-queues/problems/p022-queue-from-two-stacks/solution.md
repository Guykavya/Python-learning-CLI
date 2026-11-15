## Approach

The inbox receives new items; the outbox delivers old ones. When the outbox runs dry, pour the whole inbox into it: the reversal puts the oldest item on top. Never pour while the outbox still has items: those are older than anything in the inbox and must come out first.

## Code

```python
class QueueFromStacks:
    def __init__(self):
        self.inbox = []
        self.outbox = []

    def push(self, x):
        self.inbox.append(x)

    def _refill(self):
        if not self.outbox:
            while self.inbox:
                self.outbox.append(self.inbox.pop())

    def pop(self):
        self._refill()
        return self.outbox.pop()

    def peek(self):
        self._refill()
        return self.outbox[-1]

    def empty(self):
        return not self.inbox and not self.outbox
```

## Complexity

One `pop` can move `n` items, but each item moves from the inbox to the outbox **at most once** in its life: it is pushed once, moved once, popped once. So `n` operations cost `O(n)` in total, which is **amortised `O(1)`** per operation. Memory is `O(n)`.

## Another way

Moving everything to the outbox for every `pop` and back to the inbox afterwards is also correct, but every pop then costs `O(n)` and the queue becomes `O(n^2)` overall: that is what the time test catches. In practice you would just use `collections.deque`; this design matters because it shows how the amortised argument works, and because some languages and interview questions only give you stacks.
