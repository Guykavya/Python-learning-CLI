## Hint 1

What should happen the second time you reach an object you have already counted? Lists cannot
go in a set, but every object has an `id()`: what could you store instead? For a dict, which two
things does it point to?

## Hint 2

```
seen = set()          # ids already counted
total = 0
todo = [obj]
while todo:
    item = todo.pop()
    if id(item) in seen: continue
    seen.add(id(item))
    total += sys.getsizeof(item)
    if item is a dict: push all keys and all values
    elif item is a list/tuple/set/frozenset: push all its items
return total
```

The `seen` check is also what makes cycles stop.
