## Approach

Only the new item can break the rule, and only against its parent. If it is smaller, swapping fixes that pair, and then the item may be smaller than its new parent, so repeat. Each swap moves the item one level up, so there are at most `log2(n)` swaps. The other items never move, except the ones on the path from `i` to the root, which each move down by one level.

## Code

```python
def sift_up(a, i):
    while i > 0:
        p = (i - 1) // 2
        if a[i] < a[p]:
            a[i], a[p] = a[p], a[i]
            i = p
        else:
            break
```

## Complexity

`O(log n)` time (the height of the tree), `O(1)` extra memory.

## Another way

Instead of swapping at each step, remember the new item `x = a[i]`, move each larger parent **down** one level into the hole, and write `x` once at the end. It does about half as many writes. `heapq` uses this idea in its C code (`_siftdown` in the Python version of the module). Note the confusing name: in `heapq` the function that moves an item **up** the tree is called `_siftdown`, because it sifts "towards index 0".
