## Approach

Rotating right by `k` cuts the list into a front piece of `n - k` nodes and a back piece of `k` nodes, and puts the back piece in front. Three facts are needed: `n` and the old tail (one walk), and the new tail (node `n - k - 1`, a second partial walk). Then three link changes: remember `new_head = new_tail.next`, end the list at `new_tail`, and link the old tail to the old head.

## Code

```python
def rotate_right(head, k):
    if head is None or head.next is None:
        return head
    n = 1
    tail = head
    while tail.next is not None:         # length and last node in one walk
        tail = tail.next
        n += 1
    k %= n
    if k == 0:
        return head
    new_tail = head
    for _ in range(n - k - 1):           # the node before the new head
        new_tail = new_tail.next
    new_head = new_tail.next
    new_tail.next = None
    tail.next = head
    return new_head
```

## Complexity

`O(n)` time, independent of `k` (thanks to `k % n`), `O(1)` extra memory.

## Another way

Close the list into a ring first (`tail.next = head`), then walk `n - k` steps from the old tail and cut there: the node after the cut is the new head. Same work, and no special case for `k % n == 0` is needed, because cutting right after the old tail restores the original list.
