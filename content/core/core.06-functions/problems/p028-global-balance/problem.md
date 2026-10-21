# A wallet with a global balance

`solution.py` starts with a module-level variable:

```python
balance = 0
```

Write two functions that **change that global variable**:

- `deposit(amount)` adds `amount` to `balance` and returns the new balance.
- `withdraw(amount)` subtracts `amount` if there is enough money and returns the new balance;
  if there is not enough, it leaves `balance` unchanged and returns `None`.

**Example**

```python
deposit(100)     # 100
deposit(50)      # 150
withdraw(30)     # 120
withdraw(500)    # None
balance          # 120
```

Without the right statement, `balance += amount` inside a function raises
`UnboundLocalError`. (The chapter explains why. Section 14 also explains why the pure version,
`new_balance = deposit(balance, amount)`, is usually the better design; here you practise
`global` so you recognise it.)
