## Hint 1

`reduce(step, items, start)` needs a `step(acc, item)` that returns the **next** accumulator.
For `group_by` the accumulator is the dict of groups so far. How can you build a new dict that
is the old one plus one changed key, without changing the old one?

## Hint 2

`{**old, k: new_value}` makes a new dict: a copy of `old` with `k` set. For the new list use
`old.get(k, []) + [item]`: `+` builds a new list, while `.append` would change the old one.
Always pass `{}` as the start value, written inside the function.

## Hint 3

```
group_by:
    step(groups, item):
        k = key(item)
        return {**groups, k: groups.get(k, []) + [item]}
    return reduce(step, items, {})

merge_counts:
    merge_two(total, more):
        result = copy of total
        for k, n in more.items(): result[k] = result.get(k, 0) + n
        return result
    return reduce(merge_two, counts, {})
```
