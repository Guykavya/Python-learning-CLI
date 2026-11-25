## Approach

`.loc` always means labels and `.iloc` always means positions. With an integer index the bare `s[3]` is a label lookup in pandas 3 (in older versions it silently switched between the two), so a reader cannot tell what you meant. Writing `.loc` or `.iloc` says it.

## Code

```python
import pandas as pd


def price_of(s, label):
    return float(s.loc[label])


def nth_price(s, n):
    return float(s.iloc[n])
```

## Complexity

O(1) for a position, and O(1) on average for a label (the index is a hash table).

## Another way

`s.get(label, default)` is a label lookup that returns a default instead of raising `KeyError`. `s.iloc[[n]]` gives a one-row Series instead of a scalar.
