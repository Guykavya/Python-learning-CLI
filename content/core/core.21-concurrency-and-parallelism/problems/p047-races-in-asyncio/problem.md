# A race condition in single-threaded asyncio

"asyncio runs on one thread, so it has no race conditions." Not true. Between two lines that
have **no** `await` between them, no other task can run. But every `await` is a point where
other tasks may run and change shared state.

`starter.py` has a `Wallet`:

```python
class Wallet:
    def __init__(self, balance, check=None):
        self.balance = balance
        self.check = check or default_check      # an async fraud check, ~10 ms

    async def spend(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        if self.balance < amount:
            return False
        await self.check(amount)                 # <- other tasks run here
        self.balance -= amount
        return True
```

Ten tasks each call `spend(30)` on a wallet holding 100 at the same moment. All ten see
`balance = 100`, all ten pass the `if`, all ten wait in the fraud check, and all ten subtract:
the balance ends at **-200**.

Copy `starter.py` to `solution.py` and fix `Wallet` with an `asyncio.Lock`, so that:

- the balance never goes negative and exactly as many spends succeed as the money allows,
- `spend` still awaits `self.check(amount)` for every spend that it approves,
- two **different** wallets do not block each other (each wallet has its own lock),
- `spend` returns `True` if the money was taken, `False` if there was not enough, and raises
  `ValueError` for `amount <= 0`, as before.

**Example**

```python
wallet = Wallet(100)
results = await asyncio.gather(*(wallet.spend(30) for _ in range(10)))
results.count(True)    # 3
wallet.balance         # 10
```
