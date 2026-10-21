## Hint 1

Take the first item. Every subset of the whole list either leaves it out or includes it. What is left in each case?

## Hint 2

Base case: the empty list has exactly one subset, the empty one. So return `[[]]`, not `[]`.

## Hint 3

```
if not items: return [[]]
first, rest = items[0], items[1:]
without = subsets(rest, max_size=max_size)
with_first = [[first] + s for s in without if max_size is None or len(s) < max_size]
return without + with_first
```
Putting `first` at the front keeps the original order inside each subset.
