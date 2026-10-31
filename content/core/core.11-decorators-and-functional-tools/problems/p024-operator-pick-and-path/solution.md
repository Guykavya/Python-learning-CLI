## Approach

- `itemgetter(*indexes)` builds a function that indexes its argument. Its return shape depends
  on how many indexes you gave, so `pick` handles the single-index case by making a one-item tuple.
- `methodcaller("split", ",")` builds a function `lambda obj: obj.split(",")`. `map` applies it
  to every item.
- `operator.getitem(a, b)` is `a[b]`. Folding it over the keys with `reduce`, starting from
  `data`, walks down one level per key. With no keys, `reduce` returns the start value.

## Code

```python
import operator
from functools import reduce


def pick(rows, *indexes):
    if not indexes:
        raise ValueError("pick needs at least one index")
    getter = operator.itemgetter(*indexes)
    if len(indexes) == 1:
        return [(getter(row),) for row in rows]
    return [getter(row) for row in rows]


def call_method(items, name, *args):
    caller = operator.methodcaller(name, *args)
    return list(map(caller, items))


def get_path(data, *keys, default=None):
    try:
        return reduce(operator.getitem, keys, data)
    except (KeyError, IndexError, TypeError):
        return default
```

## Complexity

`pick` and `call_method` are O(n) for n items. `get_path` is O(k) for k keys.

## Another way

Without `operator`:

```python
def pick(rows, *indexes):
    return [tuple(row[i] for i in indexes) for row in rows]
```

This version always gives tuples, so it has no special case. `itemgetter` is a little faster
and is the usual choice as a `key=` for `sorted`, `min` and `max`. A plain `for` loop with
`value = value[key]` does the same job as the `reduce` in `get_path`.
