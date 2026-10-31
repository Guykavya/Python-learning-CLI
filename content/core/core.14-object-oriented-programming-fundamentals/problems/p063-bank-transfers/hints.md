## Hint 1

Write the exceptions first, each with an `__init__` that stores its attributes and calls
`super().__init__(message)`. Then `Account`: put the shared amount and frozen checks into one small
helper method used by both `deposit` and `withdraw`.

## Hint 2

In `transfer`, one big `try` around the whole operation lets you turn **every** failure into a
`TransferError` in one place: `except (BankError, ValueError) as err: ... raise TransferError(...) from err`.
Inside it, the deposit needs its own small `try`: if it fails, give the money back to the source and
re-raise with a bare `raise`, so the outer `except` sees the original error.

How do you give the money back without going through `deposit`'s checks? (The source is not frozen,
because the withdrawal just worked, but writing `_balance` directly inside the same module is simplest.)

## Hint 3

```text
transfer(source_id, target_id, amount):
    line = f"{amount} {source_id}->{target_id}"
    try:
        source = self.get(source_id); target = self.get(target_id)
        if source is target: raise ValueError("cannot transfer to the same account")
        source.withdraw(amount)
        try:
            target.deposit(amount)
        except BankError:
            source._balance += amount      # undo
            raise
    except (BankError, ValueError) as err:
        log "failed {line}: {err}"
        raise TransferError(source_id, target_id, amount) from err
    log "ok {line}"
```
