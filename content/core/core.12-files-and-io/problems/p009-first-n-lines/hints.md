## Hint 1

A file object is an iterator over its lines. How can you stop a `for` loop after n lines? Is there a function in `itertools` for this?

## Hint 2

```
result = []
with open(path, encoding="utf-8") as f:
    for line in f:
        if len(result) == n: break
        result.append(line.rstrip("\n"))
return result
```
Watch out for the case `n = 0`: check before you add.
