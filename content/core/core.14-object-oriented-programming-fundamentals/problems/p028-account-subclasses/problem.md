# Savings and checking accounts

A bank has one basic account and two special kinds. Most of the code is the same for all three, so
the special kinds **inherit** from the basic one and change only what is different. Write three
classes in `solution.py`.

**`Account(owner, balance=0)`**

- Attributes: `owner`, `balance`, and `transactions`, a list that starts empty.
- `balance` must be a number of 0 or more, otherwise `ValueError`.
- `deposit(amount)`: `amount` must be above 0, otherwise `ValueError`. Adds it, appends
  `("deposit", amount)` to `transactions`, returns the new balance.
- `available()` returns how much money can be taken out right now. For a basic account that is the
  balance.
- `withdraw(amount)`: `amount` must be above 0, otherwise `ValueError`. If `amount` is more than
  `self.available()`, raise `ValueError("insufficient funds")`. Otherwise subtract it, append
  `("withdraw", amount)`, and return the new balance.

**`SavingsAccount(owner, balance=0, rate=0.04)`** is an `Account`.

- `rate` must be between 0 and 0.2 (both included), otherwise `ValueError`.
- `add_interest()` computes `interest = round(balance * rate, 2)`, adds it to the balance (round the
  new balance to 2 decimals), appends `("interest", interest)` and returns `interest`.
- At most **3 withdrawals** are allowed between two `add_interest()` calls. The 4th raises
  `ValueError("withdrawal limit reached")`. A withdrawal that fails (for example for insufficient
  funds) does not count. `add_interest()` starts a new period, so the count goes back to 0.
  Override `withdraw` and call the parent's `withdraw` with `super()` for the real work.

**`CheckingAccount(owner, balance=0, overdraft=500)`** is an `Account`.

- `overdraft` must be 0 or more, otherwise `ValueError`.
- The balance may go below 0, down to `-overdraft`. Do this by overriding `available()`:
  it returns the parent's `available()` plus `overdraft`. The parent's `withdraw` then works as
  it is.

Both subclasses must call `super().__init__(owner, balance)` so that the parent sets up `owner`,
`balance` and `transactions` and checks the balance.

**Example**

```python
s = SavingsAccount("Ravi", 1000, rate=0.05)
s.withdraw(100)        # 900
s.add_interest()       # 45.0
s.balance              # 945.0
s.transactions         # [('withdraw', 100), ('interest', 45.0)]

c = CheckingAccount("Meera", 200, overdraft=300)
c.available()          # 500
c.withdraw(450)        # -250
c.withdraw(100)        # ValueError: insufficient funds  (only 50 more is available)
c.deposit(250)         # 0
```
