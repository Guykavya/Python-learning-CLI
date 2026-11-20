## Hint 1

Look at the picture level by level. The root is at index 0, its children are at 1 and 2, the children of index 1 are 3 and 4, the children of index 2 are 5 and 6. By how much does the left child's index grow when the parent's index grows by 1? Try to write `left(i)` from the three pairs `(0, 1)`, `(1, 3)`, `(2, 5)`.

## Hint 2

`left(i) = 2 * i + 1` and `right(i) = left(i) + 1`. For the parent, undo it: both `2 * i + 1` and `2 * i + 2` must give `i` back. Subtract 1 first, then use **integer** division: `(child - 1) // 2`. Check it for the children 5 and 6 of index 2.

## Hint 3

```
parent(i)   = (i - 1) // 2
left(i)     = 2 * i + 1
right(i)    = 2 * i + 2
children(i, n):
    result = []
    for c in (left(i), right(i)):      # left first
        if c < n:                      # exists only if the index is inside the heap
            result.append(c)
    return result
```
