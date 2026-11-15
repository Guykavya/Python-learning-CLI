## Hint 1

Decide about each item in turn: take it or leave it. What do you need to remember about the items you already decided? (Only their sum, or the remaining target.)

## Hint 2

If the remaining target is 0, the items chosen so far already form an answer: you can stop. Otherwise, if no items are left, this branch fails.

## Hint 3

```
def go(i, remaining):
    if remaining == 0: return True
    if i == len(nums): return False
    return go(i + 1, remaining - nums[i]) or go(i + 1, remaining)
```
`or` stops at the first `True`, which is the early exit.
