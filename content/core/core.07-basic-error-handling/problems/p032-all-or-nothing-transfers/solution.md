## Approach

"All or nothing" means the caller's dict may only change once everything is known to be fine.
Working on a copy achieves that without any exception handling at all: every failure raises
before `balances.update(work)` is reached, so the caller's dict is untouched and the exception
propagates by itself. Within one transfer, all checks (including the receiver lookup) come before
the two lines that move money, so even the copy is never half-updated (section 9: validate before
changing).

## Code

```python
def apply_transfers(balances, transfers):
    """Apply all transfers in order, or none of them if any fails. Return the number applied."""
    work = dict(balances)
    for i, (sender, receiver, amount) in enumerate(transfers, start=1):
        if amount <= 0:
            raise ValueError(f"transfer {i}: amount must be positive, got {amount}")
        balance = work[sender]
        work[receiver]                      # raises KeyError if the receiver does not exist
        if balance < amount:
            raise ValueError(f"transfer {i}: {sender} has {balance}, cannot send {amount}")
        work[sender] -= amount
        work[receiver] += amount
    balances.update(work)
    return len(transfers)
```

## Complexity

O(a + t) for a accounts (the copy) and t transfers.

## Another way

Change `balances` directly, but take a snapshot first and **roll back** on failure:

```python
snapshot = dict(balances)
try:
    ...apply each transfer to balances...
except BaseException:
    balances.clear()
    balances.update(snapshot)
    raise
```

This handler is one of the rare places where catching **everything** is correct: it does not
handle or hide anything, it undoes the partial work and re-raises the very same exception with a
bare `raise`, even for Ctrl+C. The copy-and-commit version is simpler and cannot forget a path,
which is why it is the main solution. Databases call these two strategies "transactions": work
that is committed completely or rolled back completely.
