## Approach

```python
import threading


class Bank:
    def __init__(self, balances):
        self.balances = dict(balances)
        self.locks = {account: threading.Lock() for account in balances}

    def transfer(self, src, dst, amount):
        if src == dst:
            raise ValueError("source and destination must differ")
        first, second = sorted((src, dst))            # ALWAYS lock in id order
        with self.locks[first]:
            with self.locks[second]:
                if self.balances[src] < amount:
                    return False
                self.balances[src] -= amount
                self.balances[dst] += amount
                return True

    def total(self):
        return sum(self.balances.values())
```

`sorted((src, dst))` gives the same pair of locks the same order for **both** directions. Two threads that both want accounts 1 and 2 will both try lock 1 first: one wins and the other waits **without holding anything**, so nobody waits in a circle. The balance check and the update happen while both locks are held, so the total stays constant.

Example: thread A calls `transfer(1, 2, ...)`, thread B calls `transfer(2, 1, ...)`. Both lock account 1 first. B waits at the first lock while A finishes, then B proceeds.

## Complexity

`O(1)` per transfer (plus waiting).

## Another way

One global lock for the whole bank is the simplest fix and serialises all transfers. Databases detect deadlocks and abort one transaction (PostgreSQL error `40P01`); application code must then retry (problem 28).

## Why it matters

Lock ordering is the standard, always-correct way to avoid deadlocks when you must hold several locks. It costs nothing at run time.
