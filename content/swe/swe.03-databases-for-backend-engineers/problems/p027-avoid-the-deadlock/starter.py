import threading
import time


class Bank:
    def __init__(self, balances):
        self.balances = dict(balances)
        self.locks = {account: threading.Lock() for account in balances}

    def transfer(self, src, dst, amount):
        if src == dst:
            raise ValueError("source and destination must differ")
        with self.locks[src]:
            time.sleep(0.0001)                        # "a little work" while holding the first lock
            with self.locks[dst]:
                if self.balances[src] < amount:
                    return False
                self.balances[src] -= amount
                self.balances[dst] += amount
                return True

    def total(self):
        return sum(self.balances.values())
