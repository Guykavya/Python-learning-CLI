## Hint 1

For each item you make one decision: in or out. How many leaves does a tree of `n` yes/no decisions have?

## Hint 2

The "choose the next item from the rest" view: every call records the current `path` as an answer, then tries every item at position `start` or later, recursing with `i + 1`.

## Hint 3

```
def go(start):
    result.append(path[:])          # a copy!
    for i in range(start, len(nums)):
        path.append(nums[i]); go(i + 1); path.pop()
go(0)
```
