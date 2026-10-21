## Hint 1

How many `input()` calls does one operation need? What should happen to the balance when an operation is refused?

## Hint 2

Loop `n` times. In each round read the letter line and the amount line. Then use one `if / elif / elif / else`
chain in the order given: unknown letter, bad amount, withdrawal too big, and finally "apply it".
Only the last branch changes the balance.

## Hint 3

```
balance = read int, n = read int
repeat n times:
    op = read line, amount = read int
    if op != "D" and op != "W": print "unknown operation"
    elif amount <= 0: print "invalid amount"
    elif op == "W" and amount > balance: print "declined"
    else:
        if op == "D": balance += amount
        else: balance -= amount
        print "balance", balance
print "final", balance
```
