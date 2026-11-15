## Approach

Two cases. An empty list has no last node: the new node becomes the head, so return it. A non-empty list has a last node, the one whose `next` is `None`. Walk until `cur.next is None` (stopping **on** that node), set `cur.next` to the new node, and return the old head, which did not change.

## Code

```python
def append(head, val):
    node = ListNode(val)
    if head is None:
        return node                 # the new node is the whole list
    cur = head
    while cur.next is not None:     # stop ON the last node
        cur = cur.next
    cur.next = node
    return head
```

## Complexity

`O(n)` time per call (one walk), `O(1)` extra memory. Building a list of `n` values with repeated `append` costs `1 + 2 + ... + n`, which is `O(n^2)`.

## Another way

Keep a **tail pointer** next to the head, as the `LinkedList` class of the chapter (section 3) and problem 7 do: then `append` is `tail.next = node; tail = node`, which is `O(1)`. With a dummy node you can also avoid the empty-list special case: `dummy = ListNode(0, head)`, walk from `dummy`, link, and return `dummy.next`.
