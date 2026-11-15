## Hint 1

Keep a `path` list of characters. When is the path a complete answer? What do you store then: the list, or a string made from it?

## Hint 2

At each level loop over `"01"`: append the character, recurse, pop it. Trying `"0"` before `"1"` gives dictionary order.

## Hint 3

```
def go():
    if len(path) == n: result.append("".join(path)); return
    for ch in "01":
        path.append(ch); go(); path.pop()
```
