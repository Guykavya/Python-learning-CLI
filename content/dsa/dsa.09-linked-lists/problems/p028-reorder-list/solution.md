## Approach

The result takes nodes alternately from the front and from the back. The back cannot be walked backwards, so reverse it:

1. find the end of the first half (`slow`), and cut after it: `1 -> 2 -> 3` and `4 -> 5`;
2. reverse the second half: `5 -> 4`;
3. weave: `1`, then `5`, then `2`, then `4`, then `3`. Per round two links change, and the two "next" nodes are saved first.

The first half has the same number of nodes as the second or one more, so the weave can stop when the second half runs out: the first half's last node (`slow`) already points at `None` after the cut.

## Code

```python
def reorder_list(head):
    if head is None or head.next is None:
        return None
    slow, fast = head, head.next
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
    second = slow.next
    slow.next = None                     # cut: the first half ends at slow
    prev = None                          # reverse the second half
    while second is not None:
        nxt = second.next
        second.next = prev
        prev = second
        second = nxt
    first, second = head, prev
    while second is not None:            # weave: first, last, second, second-last, ...
        n1 = first.next
        n2 = second.next
        first.next = second
        second.next = n1
        first = n1
        second = n2
    return None
```

## Complexity

`O(n)` time (three passes), `O(1)` extra memory.

## Another way

Put the nodes into a Python list `ns`, then link `ns[0], ns[-1], ns[1], ns[-2], ...` with two indexes moving towards each other, and set the last one's `next` to `None`. It is easy to get right, but uses `O(n)` memory (the memory test rejects it here). A deque of nodes with `popleft()`/`pop()` alternately gives the same idea.
