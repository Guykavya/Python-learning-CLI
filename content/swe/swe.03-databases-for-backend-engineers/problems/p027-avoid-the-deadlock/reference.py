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
