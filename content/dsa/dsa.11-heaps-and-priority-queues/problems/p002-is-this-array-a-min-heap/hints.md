## Hint 1

The heap rule is about **parent versus child**. For which pairs `(parent, child)` of indexes must the rule hold? Take the list `[1, 3, 2, 7, 4, 5, 6]` and write down the pairs: which index is the parent of index 5? Of index 4?

## Hint 2

Instead of asking "do my children obey me?" for every parent, ask for every item from index 1 to the end: "is my parent less than or equal to me?" Then every item has exactly one parent, you never run off the end of the list, and equal items need no special case.

## Hint 3

```
for i in range(1, len(a)):
    p = (i - 1) // 2
    if a[p] > a[i]:          # the parent is bigger than its child: broken
        return False
return True
```
