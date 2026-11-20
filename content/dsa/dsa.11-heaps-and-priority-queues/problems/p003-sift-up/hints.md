## Hint 1

Draw the heap `[2, 5, 3, 9, 6, 1]` as a tree. The new item `1` is the right child of `3`. Which node do you compare it with first? What do you compare next, after the swap, and when do you stop?

## Hint 2

You need a loop that keeps going while two things are true: you are not at the root, and the item is smaller than its parent. After each swap the item has a **new index**: do not forget to update `i`. The parent of index `i` is `(i - 1) // 2`.

## Hint 3

```
while i > 0:
    p = (i - 1) // 2
    if a[i] < a[p]:
        swap a[i] and a[p]
        i = p                  # the item now lives where its parent was
    else:
        break                  # parent is not larger: the heap property holds again
```
