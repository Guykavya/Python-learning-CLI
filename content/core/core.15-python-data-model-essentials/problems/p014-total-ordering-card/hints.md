## Hint 1

Strings like `"10"` and `"J"` do not sort by rank. How can you turn a rank into a number? A list of all ranks and `list.index(rank)` is one way.

## Hint 2

Build a sort key `(rank_index, suit_index)` once in `__init__`. Then `__eq__`, `__lt__` and `__hash__` all use that key. Put `@total_ordering` above the class.

## Hint 3

```
RANKS = ["2", ..., "A"] ; SUITS = [...]
__init__: validate; self._key = (RANKS.index(rank), SUITS.index(suit))
__eq__:  NotImplemented for non-Card ; self._key == other._key
__lt__:  NotImplemented for non-Card ; self._key < other._key
__hash__: hash(self._key)
```
