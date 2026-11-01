import asyncio


async def default_check(amount):
    """Pretend to ask a fraud-check service (network I/O)."""
    await asyncio.sleep(0.01)


class Wallet:
    def __init__(self, balance, check=None):
        self.balance = balance
        self.check = check or default_check
        self._lock = asyncio.Lock()     # one lock per wallet

    async def spend(self, amount):
        """Take `amount` if there is enough money. Return True if taken, else False."""
        if amount <= 0:
            raise ValueError("amount must be positive")
        async with self._lock:          # check, wait and subtract as one step
            if self.balance < amount:
                return False
            await self.check(amount)
            self.balance -= amount
            return True
