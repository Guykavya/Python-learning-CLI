## Hint 1

Use an `inbox` for pushes and an `outbox` for pops. Moving everything from `inbox` to `outbox` puts the oldest item on top of `outbox`. But if `outbox` still holds items, are they older or newer than everything in `inbox`?

## Hint 2

Refill only when the outbox is empty:

```
def _refill(self):
    if not self.outbox:
        while self.inbox:
            self.outbox.append(self.inbox.pop())
pop:  self._refill(); return self.outbox.pop()
peek: self._refill(); return self.outbox[-1]
empty: both lists are empty
```
