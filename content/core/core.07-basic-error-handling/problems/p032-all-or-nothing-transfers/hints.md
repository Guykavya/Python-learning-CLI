## Hint 1

The safest way to guarantee "nothing changes on failure" is to never touch `balances` until you
know everything worked. What could you work on instead?

## Hint 2

Work on a copy, `dict(balances)`. If any check raises, the exception simply propagates and the
caller's dict was never touched. If the loop finishes, copy the results back with
`balances.update(...)`.

## Hint 3

```
work = dict(balances)
for i, (sender, receiver, amount) in enumerate(transfers, start=1):
    if amount <= 0: raise ValueError(...)
    balance = work[sender]        # KeyError if missing
    work[receiver]                # KeyError if missing, checked before changing anything
    if balance < amount: raise ValueError(...)
    move the money in work
balances.update(work)
return len(transfers)
```
