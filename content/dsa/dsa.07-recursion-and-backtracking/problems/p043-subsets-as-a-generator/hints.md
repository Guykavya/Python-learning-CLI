## Hint 1

Start from the list version of `subsets` (view 2). Replace `result.append(path[:])` with `yield path[:]`.

## Hint 2

A recursive call to a generator function only creates a generator; nothing runs until someone iterates it. Use `yield from go(i + 1)` to pass every subset of the inner call outwards.

## Hint 3

```
def iter_subsets(items):
    path = []
    def go(start):
        yield path[:]
        for i in range(start, len(items)):
            path.append(items[i]); yield from go(i + 1); path.pop()
    yield from go(0)
```
