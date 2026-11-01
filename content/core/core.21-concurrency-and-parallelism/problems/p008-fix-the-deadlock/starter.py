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

    def deposit(self, amount):
        with self.lock:
            self.balance += amount

    def deposit_many(self, amounts):
        with self.lock:
            for amount in amounts:
                self.deposit(amount)

    def withdraw(self, amount):
        if self.balance < amount:            # check (outside the lock)
            raise ValueError("insufficient funds")
        pause()                              # keep: between the check and the change
        with self.lock:
            self.balance -= amount


def transfer(src, dst, amount):
    with src.lock:
        pause()                              # keep: while holding the first lock
        with dst.lock:
            if src.balance < amount:
                raise ValueError("insufficient funds")
            src.balance -= amount
            dst.balance += amount
