## Hint 1

In `counted`, where can the code put a `return` so that it runs only when all items have been
yielded? What does a `for` loop over the input do when the input runs out?

## Hint 2

In `drain` you cannot use `for` or `list()`, because they catch `StopIteration` for you and hide
`.value`. Call `next()` yourself in a `while True` loop and catch the exception with a name:
`except StopIteration as e`.

## Hint 3

```
counted:
    n = 0
    for item in iterable: n += 1; yield item
    return n

drain:
    items = []
    loop for ever:
        try: items.append(next(iterator))
        except StopIteration as e: return items, e.value
```
