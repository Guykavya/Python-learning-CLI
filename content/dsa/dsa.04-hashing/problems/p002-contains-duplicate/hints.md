## Hint 1

While walking through the list, what do you need to remember about the values already passed? Which Python container answers "is x in here?" in O(1)?

## Hint 2

Keep `seen = set()`. For each `x`: if `x in seen`, you found a repeat. Otherwise `seen.add(x)`.

## Hint 3

```
seen = empty set
for x in a:
    if x in seen: print YES and stop
    add x to seen
print NO
```
