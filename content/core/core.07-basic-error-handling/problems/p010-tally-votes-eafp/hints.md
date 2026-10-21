## Hint 1

What happens when you run `counts["asha"] += 1` on an empty dict? Which exception, and what
should the handler do instead?

## Hint 2

```
for each vote:
    name = cleaned vote
    if name is empty: continue
    try:
        counts[name] += 1
    except KeyError:
        counts[name] = 1
```
