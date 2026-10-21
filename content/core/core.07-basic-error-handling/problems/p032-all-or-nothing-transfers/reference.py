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
