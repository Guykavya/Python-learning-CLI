## Hint 1

Run the tests against the starter. Each failure names the exception that should have been raised. Which kind of exception is it?

## Hint 2

Which check must come first if `amount` is `-5` and the balance is `100`? Think about which message the test expects for `-5`.

## Hint 3

```
if amount <= 0: raise ValueError("amount must be positive")
if amount > balance: raise ValueError("insufficient funds")
return balance - amount
```
