## Approach

The varying part (how to discount) becomes a parameter. A strategy is a function from total to
total. `percent_off` and `flat_off` are *factories of strategies*: they return a closure that
remembers `p` or `n`. `checkout` no longer knows any discount names, so adding a new discount
means writing a new function, with no edit to `checkout` (open for extension, closed for
modification).

## Code

```python
def no_discount(total):
    return total


def percent_off(p):
    def strategy(total):
        return total - total * p / 100
    return strategy


def flat_off(n):
    def strategy(total):
        return max(total - n, 0)
    return strategy


def checkout(items, strategy=no_discount):
    return round(strategy(sum(items)), 2)
```

## Complexity

O(len(items)) for the sum; each strategy is O(1).

## Another way

`functools.partial` builds the same thing without writing closures:

```python
from functools import partial

def _percent(p, total):
    return total - total * p / 100

def percent_off(p):
    return partial(_percent, p)
```

For a strategy that needs several settings *and* state (a counter, a log), a small class with
`__call__` works too. Use a class only when a plain function and a closure stop being enough.
