# spec and autospec

A plain `Mock()` accepts **any** attribute and **any** arguments, so a typo like `bank.widthdraw(...)`
"works" and the test stays green while the real code crashes. `create_autospec(Bank, instance=True)`
builds a mock that copies the real class: unknown attributes raise `AttributeError` and calls with the
wrong number of arguments raise `TypeError`.

```python
class Bank:
    def withdraw(self, account, amount): ...   # returns True if the money was taken, else False
    def deposit(self, account, amount): ...    # adds the money
    def balance(self, account): ...            # current balance
```

In `solution.py` write two functions:

1. `make_bank(bank_class)` returns `create_autospec(bank_class, instance=True)` set up so that
   `withdraw(...)` returns `True` and `balance(...)` returns `100` unless a test says otherwise.
2. `transfer(bank, src, dst, amount)` moves money: if `amount <= 0` raise `ValueError` (before
   calling the bank at all); call `bank.withdraw(src, amount)`; only if it returned `True`, call
   `bank.deposit(dst, amount)` and return `True`; otherwise return `False` and deposit nothing.

**Example**

```python
bank = make_bank(Bank)
bank.balance("a")            # 100
bank.widthdraw("a", 5)       # AttributeError: Mock object has no attribute 'widthdraw'
bank.deposit("a")            # TypeError: missing a required argument: 'amount'
transfer(bank, "a", "b", 50) # True, and bank.deposit was called with ("b", 50)
```
