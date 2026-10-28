## Hint 1

Without `__contains__` Python cannot say whether `5` is in an `Interval`. Which method does `5 in obj` call? What are its parameters and what does it return?

## Hint 2

For `Interval`, compare `self.lo <= item <= self.hi` after checking the type. For `WordSet`, normalise the stored words with `casefold()` once in `__init__` (a set makes lookup fast), and normalise the item the same way.

## Hint 3

```
class Interval:  __contains__(self, item):
    not int/float -> False ; return lo <= item <= hi
class WordSet:   __init__: self._words = {w.casefold() for w in words}
    __contains__(self, item): not str -> False ; item.casefold() in self._words
```
