## Hint 1

A group's children are in `eg.exceptions`. Each child is either a leaf or another group. That is a
tree, and trees are easiest with recursion: what do you return for a leaf at index `i`? What do you do
with the list you get back from a recursive call on a sub-group at index `i`?

## Hint 2

`eg.split(T)` returns two groups (or `None`) that keep the nesting. You already have a function that
turns a group into its leaves, so you only need to handle `None`.

## Hint 3

```text
leaves(eg):
    if eg is not a BaseExceptionGroup: raise TypeError(...)
    result = []
    for i, exc in enumerate(eg.exceptions):
        if exc is a BaseExceptionGroup:
            for path, leaf in leaves(exc): result.append(((i,) + path, leaf))
        else:
            result.append(((i,), exc))
    return result

partition(eg, T):
    match, rest = eg.split(T)
    return messages(match), messages(rest)    # messages(None) -> []
```
