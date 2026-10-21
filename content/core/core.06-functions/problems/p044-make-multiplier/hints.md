## Hint 1

Define a function **inside** `make_multiplier`. Which variable from the outer function does it use?

## Hint 2

```
def make_multiplier(factor):
    def multiply(n):
        return n * factor
    return multiply        # the function, no parentheses
```
