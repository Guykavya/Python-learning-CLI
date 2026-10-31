## Hint 1

To know if you have seen something before, you need a memory. Which collection answers
"is this in here?" fast?

## Hint 2

What do you store in that memory when `key` is given: the item, or `key(item)`?
And what do you yield?

## Hint 3

```
seen = empty set
for item in iterable:
    marker = item if key is None else key(item)
    if marker not in seen:
        add marker to seen
        yield item
```
