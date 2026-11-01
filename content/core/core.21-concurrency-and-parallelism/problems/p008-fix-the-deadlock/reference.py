import threading
import time


def pause():
    """Stands for a slow fraud check or database call. Keep every call."""
    time.sleep(0.01)


class Account:
    def __init__(self, number, balance=0):
        self.number = number
        self.balance = balance
        self.lock = threading.Lock()

    # Helpers that assume the caller already holds self.lock.
    def _add(self, amount):
        self.balance += amount

    def _take(self, amount):
        if self.balance < amount:
            raise ValueError("insufficient funds")
        self.balance -= amount

    def deposit(self, amount):
        with self.lock:
            self._add(amount)

    def deposit_many(self, amounts):
        with self.lock:
            for amount in amounts:
                self._add(amount)          # not self.deposit(): the lock is not re-entrant

    def withdraw(self, amount):
        with self.lock:                    # check and change under ONE lock
            if self.balance < amount:
                raise ValueError("insufficient funds")
            pause()
            self.balance -= amount


def transfer(src, dst, amount):
    if src is dst:
        raise ValueError("cannot transfer to the same account")
    first, second = sorted((src, dst), key=lambda acc: acc.number)
    with first.lock:                       # every thread locks the lower number first
        pause()
        with second.lock:
            src._take(amount)              # raises before anything changes
            dst._add(amount)
