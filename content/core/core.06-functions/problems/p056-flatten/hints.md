## Hint 1

For each item: if it is a list, what should you do with it? If it is not?

## Hint 2

Trust the recursion: `flatten(item)` returns that sub-list's items, already flat. Extend your result with them.

## Hint 3

```
result = []
for item in nested:
    if isinstance(item, list):
        result.extend(flatten(item))
    else:
        result.append(item)
return result
```
