## Hint 1

Mark every `await` in `spend`. Between the line that **checks** the balance and the line that
**changes** it, is there an `await`? What can other tasks do there, and what balance do they
see? Which lines must therefore run as one uninterrupted step for a given wallet?

## Hint 2

An `asyncio.Lock` lets only one task at a time inside `async with lock:`; the others wait at
that line (without blocking the loop). Put the check, the `await self.check(...)` and the
subtraction inside it. One lock **per wallet**: create it in `__init__`.

```
__init__: self._lock = asyncio.Lock()

spend(amount):
    if amount <= 0: raise ValueError
    async with self._lock:
        if self.balance < amount: return False
        await self.check(amount)
        self.balance -= amount
        return True
```
