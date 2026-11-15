## Hint 1

The engine is the template with the three questions turned into calls:
```
def go():
    if is_done(path): result.append(path[:])
    for option in choices(path):
        if not is_valid(path, option): continue
        path.append(option); go(); path.pop()
```

## Hint 2

For `subsets`, work with **positions**: the path holds indexes, `choices(path)` = `range(last + 1, n)` where `last` is `path[-1]` (or `-1` for the empty path). Convert each recorded index list to values at the end.

## Hint 3

For `permutations`, `choices(path)` = `range(n)`, `is_valid(path, i)` = `i not in path`, `is_done(path)` = `len(path) == n`. Convert indexes to values at the end.
