## Approach

Write the template once with the three questions as parameters. Each problem then becomes three small functions. Working with **indexes** in the path keeps the users simple: the order rule for subsets is "next index > last index", and "unused" for permutations is "index not in path".

## Code

```python
def backtrack(choices, is_valid, is_done):
    result, path = [], []

    def go():
        if is_done(path):
            result.append(path[:])            # record a copy
        for option in choices(path):
            if not is_valid(path, option):
                continue                      # prune
            path.append(option)               # choose
            go()                              # explore
            path.pop()                        # un-choose

    go()
    return result


def subsets(nums):
    n = len(nums)

    def choices(path):
        last = path[-1] if path else -1
        return range(last + 1, n)

    found = backtrack(choices, lambda path, i: True, lambda path: True)
    return [[nums[i] for i in idx] for idx in found]


def permutations(nums):
    n = len(nums)
    found = backtrack(lambda path: range(n) if len(path) < n else [],
                      lambda path, i: i not in path,
                      lambda path: len(path) == n)
    return [[nums[i] for i in idx] for idx in found]
```

## Complexity

The engine adds only a constant factor (a few function calls per node) over hand-written code. `subsets` makes `2^n` nodes; `permutations` makes about `e * n!` nodes, and `i not in path` costs `O(n)` per test.

## Another way

Let the engine **yield** answers instead of collecting them (`yield path[:]` and `yield from go()`), so callers can stop early (chapter section 15). Or pass a `state` object to the callbacks for faster checks (a `used` set instead of `i not in path`).
