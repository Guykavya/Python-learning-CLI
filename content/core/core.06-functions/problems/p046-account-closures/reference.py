def make_account(balance=0):
    """Return {'deposit': f, 'withdraw': f, 'balance': f} sharing one private balance."""

    def deposit(amount):
        nonlocal balance
        if amount <= 0:
            return None
        balance += amount
        return balance

    def withdraw(amount):
        nonlocal balance
        if amount <= 0 or amount > balance:
            return None
        balance -= amount
        return balance

    def current():
        return balance

    return {"deposit": deposit, "withdraw": withdraw, "balance": current}
