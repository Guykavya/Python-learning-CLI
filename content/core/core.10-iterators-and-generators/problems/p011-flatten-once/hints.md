## Hint 1

There are two `chain` forms: `chain(a, b, c)` takes separate arguments. Which form do you need when you already have *one* iterable that holds the lists?

## Hint 2

`chain.from_iterable(list_of_lists)` lazily glues the inner iterables together. Wrap in `list(...)`.

## Hint 3

```
from itertools import chain
return list(chain.from_iterable(list_of_lists))
```
