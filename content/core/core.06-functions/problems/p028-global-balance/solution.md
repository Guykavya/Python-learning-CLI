## Approach

Any assignment to `balance` inside a function makes it local for the whole function, unless the
function says `global balance`. With the declaration, `balance += amount` reads and writes the
module's variable. `withdraw` checks first and returns `None` early when the money is not there.

## Code

```python
balance = 0


def deposit(amount):
    """Add amount to the global balance and return the new balance."""
    global balance
    balance += amount
    return balance


def withdraw(amount):
    """Subtract amount from the global balance if there is enough; return the new balance or None."""
    global balance
    if amount > balance:
        return None
    balance -= amount
    return balance
```

## Complexity

O(1).

## Another way

The pure design avoids globals entirely: `def deposit(balance, amount): return balance + amount`,
called as `balance = deposit(balance, 100)`. Tests then need no `setup_function` to reset hidden
state, which is exactly why pure functions are easier to test.
