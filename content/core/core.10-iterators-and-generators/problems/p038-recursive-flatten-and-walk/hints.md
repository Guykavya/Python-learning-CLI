## Hint 1

What is the smallest case? An item that is not a list or tuple: you just yield it. What is the
bigger case? An inner list: it is the same problem again, only smaller. Which tool hands all items
of a smaller generator up to your caller?

## Hint 2

In `walk`, the recursive call must know the path so far. Pass it as a second argument. When you go
into folder `src`, what should the prefix be for the files inside it?

## Hint 3

```
flatten(data):
    for item in data:
        if item is a list or tuple: yield from flatten(item)
        else: yield item

walk(tree, prefix=""):
    for name, value in tree.items():
        path = prefix + name
        if value is a dict: yield from walk(value, path + "/")
        else: yield (path, value)
```
