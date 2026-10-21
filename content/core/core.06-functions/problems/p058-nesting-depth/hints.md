## Hint 1

Which inputs can you answer without recursion? (There are two kinds.)

## Hint 2

For a container, you need the deepest item. Recurse on every item and take the maximum. What if there are no items?

## Hint 3

```
if not isinstance(data, (list, tuple)): return 0
deepest = 0
for item in data:
    deepest = max(deepest, depth(item))
return 1 + deepest
```
`isinstance` accepts a tuple of types.
