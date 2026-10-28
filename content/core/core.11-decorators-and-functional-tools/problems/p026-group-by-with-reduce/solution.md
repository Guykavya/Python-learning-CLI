## Approach

Each function is "fold the items into one dict". The step function gets the dict so far and
one item, and returns a new dict. It never changes the dict it was given, so no earlier
result can change by accident.

The start value `{}` is written inside the call to `reduce`, so each call starts with its own
new empty dict.

## Code

```python
from functools import reduce


def group_by(items, key):
    def step(groups, item):
        k = key(item)
        return {**groups, k: groups.get(k, []) + [item]}
    return reduce(step, items, {})


def count_by(items, key):
    def step(counts, item):
        k = key(item)
        return {**counts, k: counts.get(k, 0) + 1}
    return reduce(step, items, {})


def merge_counts(*counts):
    def merge_two(total, more):
        result = dict(total)
        for k, n in more.items():
            result[k] = result.get(k, 0) + n
        return result
    return reduce(merge_two, counts, {})
```

## Complexity

The pure `group_by` and `count_by` copy the dict on every step, so they are O(n * g) for n items
and g groups. That is the price of never mutating. `merge_counts` is O(total number of keys
times number of dicts).

## Another way

The fast, ordinary way mutates **one local dict** that nobody else can see:

```python
def group_by(items, key):
    groups = {}
    for item in items:
        groups.setdefault(key(item), []).append(item)
    return groups
```

This is O(n) and still safe, because the dict is created inside the call. "Pure" is about what
the caller can see: no argument changes and the same input gives the same output. Inside the
function a local mutable dict is fine. Use the `reduce` version when you want each step to be a
small pure function you can test on its own.
