## Hint 1

Where does the balance live so that all three inner functions share it?

## Hint 2

Which inner functions **rebind** the balance (and so need `nonlocal`), and which only read it?

## Hint 3

```
def make_account(balance=0):
    def deposit(amount):
        nonlocal balance
        if amount <= 0: return None
        balance += amount
        return balance
    ... withdraw similarly ...
    def current():
        return balance
    return {"deposit": deposit, "withdraw": withdraw, "balance": current}
```
