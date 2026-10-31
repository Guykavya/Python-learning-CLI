- Forgetting the undo. When B is frozen, A's money is gone: the transfer was not atomic.
- Undoing with `source.deposit(amount)` inside an `except` that also catches its failure, or undoing
  for errors that happened **before** the withdrawal (then money is created from nothing).
- `raise TransferError(...)` without `from err`. The traceback then says "during handling of the above
  exception, another exception occurred", and `__cause__` is `None`.
- Catching `Exception` around the transfer. A real bug in your code (a `NameError`) would be turned into
  a harmless-looking `TransferError`.
- A `balance` setter, or a plain `self.balance` attribute. Then anyone can write `acc.balance = 10**6`.
- Logging the `TransferError` message in the statement. The line must show the **cause**: why it failed.
- Forgetting that `True` is an `int`. `deposit(True)` must be rejected.
