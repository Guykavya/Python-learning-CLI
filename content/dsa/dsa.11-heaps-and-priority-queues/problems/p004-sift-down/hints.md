## Hint 1

Take `[9, 3, 2, 7, 4, 5, 6]` with `i = 0`. The item `9` has two children, `3` and `2`. Which one must it swap with, and why not the other? After the swap, which index does the `9` have, and which children does it have now?

## Hint 2

Write the loop in three parts: (1) find the index `smallest` among `i`, `left` and `right`, but look at a child only if its index is `< n`; (2) if `smallest` is still `i`, nothing is smaller: stop; (3) otherwise swap and set `i = smallest`. The sentinel in the tests sits at an index `>= n`: if you test `< len(a)` instead of `< n`, you will pull it into the heap.

## Hint 3

```
while True:
    smallest = i
    l = 2*i + 1;  r = 2*i + 2
    if l < n and a[l] < a[smallest]: smallest = l
    if r < n and a[r] < a[smallest]: smallest = r      # compares with the best so far, not with a[i]
    if smallest == i: break
    swap a[i] and a[smallest]
    i = smallest
```
