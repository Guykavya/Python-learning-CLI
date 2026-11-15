## Approach

1. A dummy node makes "the node before the range" exist even when `left = 1`. Walk `left - 1` steps from it to reach `before`.
2. `first = before.next` is the first node of the range; after the reversal it will be the **last** one.
3. Reverse `right - left + 1` nodes with the usual loop. Afterwards `prev` is the new first node of the range and `cur` is the first node after it (or `None`).
4. Stitch: `before.next = prev` and `first.next = cur`.

## Code

```python
def reverse_between(head, left, right):
    dummy = ListNode(0, head)
    before = dummy
    for _ in range(left - 1):
        before = before.next                 # the node just before position left
    first = before.next                      # becomes the last node of the reversed part
    prev, cur = None, first
    for _ in range(right - left + 1):
        nxt = cur.next
        cur.next = prev
        prev = cur
        cur = nxt
    before.next = prev                       # connect the front to the reversed part
    first.next = cur                         # connect the reversed part to the rest
    return dummy.next
```

## Complexity

`O(right)` time, at most `O(n)`, in one pass. `O(1)` extra memory.

## Another way

The "insert at front" method: stand on `before`, and `right - left` times move the node after `first` to just after `before`:

```python
for _ in range(right - left):
    move = first.next
    first.next = move.next
    move.next = before.next
    before.next = move
```

Each round pulls one more node to the front of the range. It needs no stitching step at the end, because `first` always stays connected to the rest.
