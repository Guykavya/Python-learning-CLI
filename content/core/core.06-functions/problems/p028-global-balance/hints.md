## Hint 1

Why does `balance += amount` make `balance` a local variable of the function?

## Hint 2

```
def deposit(amount):
    global balance
    balance += amount
    return balance
```
`withdraw` needs `global balance` too, and a guard clause for "not enough money".
