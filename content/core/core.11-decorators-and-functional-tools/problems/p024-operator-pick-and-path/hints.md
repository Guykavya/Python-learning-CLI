## Hint 1

For `pick`: what does `operator.itemgetter(1)(("ann", 31))` return, and what does
`operator.itemgetter(0, 1)(("ann", 31))` return? How can you tell the two cases apart by
looking at `len(indexes)`?

## Hint 2

For `get_path`: `reduce(f, keys, data)` computes `f(f(f(data, k1), k2), k3)`. Which function
from `operator` does `value[key]`? Put the whole `reduce` inside `try` and list the three
exception types in one `except (A, B, C):`.

## Hint 3

```
pick:
    if no indexes: raise ValueError
    getter = itemgetter(*indexes)
    if one index: return [(getter(row),) for row in rows]
    return [getter(row) for row in rows]

call_method:
    caller = methodcaller(name, *args)
    return list(map(caller, items))

get_path:
    try: return reduce(operator.getitem, keys, data)
    except (KeyError, IndexError, TypeError): return default
```
