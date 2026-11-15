## Hint 1

Look at one item at a time. If it is not a list, it goes straight into the result. If it is a list, what do you need from it?

## Hint 2

`flatten(item)` already gives the flat values of an inner list. Add them to the result with `extend`.

## Hint 3

```
result = []
for item in xs:
    if isinstance(item, list): result.extend(flatten(item))
    else: result.append(item)
return result
```
