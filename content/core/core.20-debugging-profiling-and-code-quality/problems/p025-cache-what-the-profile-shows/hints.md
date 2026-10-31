## Hint 1

What are the **arguments** of `count`, and are they all hashable? (A cache is a dictionary
keyed by the arguments.) Which function should get the cache: `ways`, which receives a list, or
`count`, which receives a tuple?

## Hint 2

Put `@cache` on `count`, the recursive function the profile blames, and leave `ways` as the
thin wrapper that turns the list into a tuple. The coins are part of the arguments, so two
different coin lists never share a cached answer.

```
from functools import cache

def ways(amount, coins):
    return count(amount, tuple(coins), 0)

@cache
def count(amount, coins, i):
    ... same body ...
```
