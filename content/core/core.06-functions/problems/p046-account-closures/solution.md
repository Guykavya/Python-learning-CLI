## Approach

The parameter `balance` is a local of `make_account`. All three inner functions refer to it, so
they share one cell. The two that change it declare `nonlocal balance`; `current` only reads it.
Returning the functions in a dict gives the caller named operations on hidden state, which nothing
else in the program can reach.

## Code

```python
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
```

## Complexity

O(1) per operation.

## Another way

Return a tuple `(deposit, withdraw, current)` and unpack it at the call site. A dict is easier to
extend and to read (`acct["deposit"]`), and it is the same idea as a dispatch table. A later
module shows classes, which are the usual tool for state plus behaviour.
