## Approach

This is the classic **check-then-act** race. The check (`balance < amount`) and the act
(`balance -= amount`) belong together: the act is correct only if the balance has not changed
since the check. In asyncio, code between two `await`s cannot be interrupted, but here an
`await` sits right between them.

Ten tasks, without the lock:

| Step | What happens | balance |
|---|---|---|
| 1 | task 1 checks 100 >= 30, awaits the fraud check | 100 |
| 2-10 | tasks 2..10 each check 100 >= 30 (nobody has subtracted yet), await | 100 |
| 11-20 | each check finishes, each task subtracts 30 | 70, 40, 10, -20, ... -200 |

With `async with self._lock:` around the three lines, task 2 waits at the lock until task 1 has
subtracted and left, so task 2's check sees 70. `asyncio.Lock` hands the lock to waiters in
the order they arrived, which is why the *first* five callers win in the 50/10 test.

`async with` releases the lock even if `self.check` raises, so one failed fraud check does not
leave the wallet locked forever.

The lock is created in `__init__`, so each wallet has its own: spending from wallet A never
waits for wallet B. The `amount <= 0` check needs no lock (it reads no shared state), so it
stays outside.

## Code

```python
import asyncio


async def default_check(amount):
    await asyncio.sleep(0.01)


class Wallet:
    def __init__(self, balance, check=None):
        self.balance = balance
        self.check = check or default_check
        self._lock = asyncio.Lock()

    async def spend(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        async with self._lock:
            if self.balance < amount:
                return False
            await self.check(amount)
            self.balance -= amount
            return True
```

## Complexity

O(1) work per spend. Spends on one wallet are serialized: n concurrent spends take about n
fraud-check times. That is the price of correctness, paid only per wallet.

## Another way

**Reserve first, then check.** Subtract before the `await`, and give the money back if the
check fails:

```python
if self.balance < amount:
    return False
self.balance -= amount          # no await between check and act: atomic in asyncio
try:
    await self.check(amount)
except BaseException:
    self.balance += amount      # refund on failure or cancellation
    raise
return True
```

This needs no lock and lets several checks of one wallet run at the same time. But it only
works because asyncio cannot switch tasks between the `if` and the subtraction; with
**threads** the same two lines would still race, and you would need a `threading.Lock`.
