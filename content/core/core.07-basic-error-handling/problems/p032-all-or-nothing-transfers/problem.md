# All-or-nothing money transfers

A bank applies a batch of transfers at the end of the day. Write
`apply_transfers(balances, transfers)` where `balances` is a dict from account name to amount and
`transfers` is a list of `(sender, receiver, amount)` tuples.

Apply the transfers **in order**: each takes `amount` from `sender` and adds it to `receiver`.
A later transfer may spend money received in an earlier one. Number the transfers from 1.

- An account that does not exist: let the `KeyError` from the dict lookup propagate (its argument
  is the missing name).
- `amount` not greater than 0:
  `ValueError(f"transfer {i}: amount must be positive, got {amount}")`
- The sender does not have enough at that point:
  `ValueError(f"transfer {i}: {sender} has {balance}, cannot send {amount}")`

**All or nothing**: if any transfer fails, `balances` must be left **exactly as it was** before the
call, and the exception must reach the caller. If all succeed, update the caller's `balances` dict
itself (not a copy) and return the number of transfers applied.

**Example**

```python
accounts = {"asha": 100, "ravi": 50}
apply_transfers(accounts, [("asha", "ravi", 30), ("ravi", "asha", 70)])   # 2
accounts                                                                  # {'asha': 140, 'ravi': 10}

apply_transfers(accounts, [("asha", "ravi", 40), ("ravi", "zoya", 5)])    # raises KeyError: 'zoya'
accounts                                                                  # {'asha': 140, 'ravi': 10} unchanged
```
