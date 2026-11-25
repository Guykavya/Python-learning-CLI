## Hint 1

What does `np.cumsum([-30, -50, 40])` give, and how is that related to the balance after each transaction? How do you add the opening balance to every element at once?

## Hint 2

For the overdraft: build a boolean mask "balance below zero". `np.argmax` of a boolean array returns the position of the first `True`... but what does it return when there is no `True` at all?

## Hint 3

```text
running_balance:  t = np.asarray(txns, dtype=float);  return opening + np.cumsum(t)
first_overdraft_day:
    below = running_balance(...) < 0
    if no element of below is True: return -1
    return int(np.argmax(below))
```
