# Running balance

Chapter sections 10.5 (running totals) and 8 (boolean masks). A bank account starts with an `opening` balance. `txns` is a list or 1-D array of the day's transactions in order: positive numbers are deposits, negative numbers are withdrawals. Write two functions, **without a Python loop**.

## `running_balance(opening, txns)`

Return a NumPy array with the balance **after** each transaction: one value per transaction, dtype `float64` (even when every input is an integer), shape `(len(txns),)`. With no transactions the result is an empty `float64` array.

## `first_overdraft_day(opening, txns)`

Return the position (0-based, a Python `int`) of the first transaction after which the balance is **below zero**, or `-1` if that never happens. A balance of exactly `0` is not an overdraft.

Neither function may change the caller's `txns`.

## Example

```python
running_balance(100, [-30, -50, 40, -80, 10])
# array([ 70.,  20.,  60., -20., -10.])
first_overdraft_day(100, [-30, -50, 40, -80, 10])
# 3
first_overdraft_day(100, [-30, -70])
# -1   (the balance touches 0 but never goes below)
```
