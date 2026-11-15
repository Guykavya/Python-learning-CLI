## Approach

Walk the chain while counting. At each node compare its value with `target`; on the first match return the counter. If the walk reaches `None`, return `-1`.

## Code

```python
def find(head, target):
    index = 0
    cur = head
    while cur is not None:
        if cur.val == target:
            return index
        index += 1
        cur = cur.next
    return -1
```

## Complexity

`O(n)` time in the worst case (not found, or found at the end); `O(1)` extra memory. A linked list has no faster search, even when sorted: binary search needs jumps to the middle, and a jump costs a walk.

## Another way

If the chain had an `__iter__` (as the `LinkedList` class of section 3 has), you could write `for i, v in enumerate(lst): if v == target: return i`. That is the same walk; the generator hides the `cur = cur.next` line.
