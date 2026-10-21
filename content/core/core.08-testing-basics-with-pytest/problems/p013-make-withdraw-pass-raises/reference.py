def withdraw(balance, amount):
    """Return the balance after taking amount out. Raise ValueError for bad amounts."""
    if amount <= 0:
        raise ValueError("amount must be positive")
    if amount > balance:
        raise ValueError("insufficient funds")
    return balance - amount
